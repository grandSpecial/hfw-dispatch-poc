from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from twilio.rest import Client
import os
import requests
import os
import json
import re

from app.models import Case, User
from app.forms import BaseUserCreationForm
from app.distance import haversine

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# HELPER FUNCTION
def geocode_address(address):
	# Build the URL
	base_url = "https://maps.googleapis.com/maps/api/geocode/json"
	params = {
		"address": address,
		"key": GOOGLE_MAPS_API_KEY
	}
	response = requests.get(base_url, params=params)

	# Check if the request was successful
	if response.status_code == 200:
		return response.json()
	else:
		return None

def clean_number(phone_string):
	numbers = re.findall(r'\d+', phone_string)
	return ''.join(numbers)

def index(request):
	return render(request, "index.html")

def report(request, id=None):
	animal_types = ["Seabird", "Raptor", "Songbird", 
	"Waterfowl", "Other bird", "Small Rodent", 
	"Raccoon", "Fox", "Squirrel", "Deer", 
	"Seal", "Other mammal", "Other"]
	if request.method == "POST":
		if not id:
			c = Case(id=Case.short_uuid())
		else:
			c = Case.objects.get(id=id)

		# Retrieve the ID from the form data
		form_id = request.POST.get('id')

		if form_id:
			try:
				c = Case.objects.get(id=form_id)
			except Case.DoesNotExist:
				c = Case(id=Case.short_uuid())
			status = "Relay"
		else:
			c = Case(id=Case.short_uuid())
			status = "Reported"

		c.animal = request.POST.get("animal-type")
		
		# Parse coordinates from the form
		report_coords = request.POST.get("coordinates").split(",")
		report_lat,report_lon = map(float, report_coords)

		# Find users within travel distance
		nearby_users = []
		# Get all logged in users and interest == "Dispatch"
		for user in User.objects.filter(interests="Dispatch").filter(logged_in=True):
			if user.home_coordinates:
				user_coords = user.home_coordinates.split(",")
				user_lat, user_lon = map(float, user_coords)
				distance = haversine(report_lon, report_lat, user_lon, user_lat)
				print(distance)
				if distance <= user.travel_distance:
					nearby_users.append(user.mobile_phone)

		messages_sent = len(nearby_users)
		pn = request.POST.get("reporter-phone-number"),
		phone_number = clean_number(str(pn))
		c.add_log_entry(
			request.POST.get("reporter-name"),
			phone_number,
			request.POST.get("notes"),
			request.POST.get("coordinates").split(","), # Store list
			status,
			messages_sent,
		)
		c.save()
		print(f"New {c.animal} case saved")

		# TODO
		# Text the nearby users with a request to pickup
		# and the URL for the case page 
		client = Client(TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN)
		# Message to be sent
		url =f"https://hfw.tbat.io/c/{c.id}"
		message_body = f"A new {c.animal} case has been reported. Please check the details at {url}"

		for phone_number in nearby_users:
			print(phone_number)
			try:
				message = client.messages.create(
					to=phone_number,
					from_=TWILIO_PHONE_NUMBER,
					body=message_body
				)
				print(f"Message sent to {phone_number}: {message.sid}")
			except Exception as e:
				print(f"Failed to send message to {phone_number}: {e}")
		
		return redirect(case, c.id)

	# if there's an ID in the url then its a relay request 
	# get the user information and prepopulate the form
	if id:
		c = Case.objects.get(id=id)
		return render(request, 'report_.html', {'case':c,
			"GOOGLE_MAPS_API_KEY":GOOGLE_MAPS_API_KEY, "animal_types":animal_types})

	return render(request, 'report_.html',
		{"GOOGLE_MAPS_API_KEY":GOOGLE_MAPS_API_KEY,"animal_types":animal_types})

@login_required
def map_view(request):
	cases = Case.objects.all().order_by("-created_on")
	map_data = [
		{"id": case.id,
		"coordinates" : case.log[0]['coordinates'], 
		"status" : case.log[0]['status'], 
		"Animals" : case.animal,
		} for case in cases
	]
	# logged in, dispatch users 
	logged_in_users = User.objects.filter(interests="Dispatch").filter(logged_in=True)
	user_data = [
		{"name":u.username,
		"coordinates":[u.home_coordinates],
		"phone":u.mobile_phone,
		} for u in logged_in_users]
	
	return render(request, 'map_.html', 
		{"cases":cases, "map_data":json.dumps(map_data),
		"GOOGLE_MAPS_API_KEY":GOOGLE_MAPS_API_KEY, "user_data": json.dumps(user_data)})

@login_required
def log(request):
	cases = Case.objects.all()
	return render(request, 'log.html', {'cases':cases})

@login_required
def case(request, id):
	case = Case.objects.get(pk=id)
	coordinates = [float(c) for c in case.log[0]['coordinates']]
	if request.method == "POST":
		user_field = request.POST.get("name-confirm")
		if user_field == request.user.username:
			status = request.POST.get("status")
			print(status)
			# Add log entry
			case.add_log_entry(
				name=request.user.first_name,
				contact_number=request.user.mobile_phone,  # Assuming contact number is stored in user profile
				message=request.POST.get("note"),
				coordinates=coordinates,  # Provide the appropriate coordinates here
				status=status,
				messages_sent=1 #indicate one text was sent as 1 volunteer has accepted
			)
			messages.success(request, f"{status} confirmed.")
		else:
			print(request.user.username)
			print(user_field)
			messages.error(request, "Invalid username entered.")

	map_data = [
		{"Coordinates": coordinates,
		 "Status": case.log[0]['status'],
		 "Animal": case.animal,
		 }
	]

	return render(request, 'case_.html', 
				  {"case": case, "map_data": map_data,
				  "GOOGLE_MAPS_API_KEY":GOOGLE_MAPS_API_KEY})

def register(request,mobile_phone=None):
	if request.method == "POST":
		form = BaseUserCreationForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)  # Don't save to DB yet
			address = form.cleaned_data.get('home_address')
			geocode_result = geocode_address(address)
			if geocode_result and geocode_result['status'] == 'OK':
				# Extract coordinates from the first result
				coordinates = geocode_result['results'][0]['geometry']['location']
				lat, lng = coordinates['lat'], coordinates['lng']
				user.home_coordinates = f"{lat}, {lng}"
			user.save()  # Now save the user to DB
			return render(request, 'index.html')
	else:
		if mobile_phone:
			form = BaseUserCreationForm(initial={'mobile_phone':mobile_phone})
		else:
			form = BaseUserCreationForm()
	return render(request, 'register.html', {'form': form,
		'GOOGLE_MAPS_API_KEY':GOOGLE_MAPS_API_KEY})
