from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
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

# HELPER FUNCTION
def geocode_address(address):
	# Build the URL
	base_url = "https://maps.googleapis.com/maps/api/geocode/json"
	params = {
		"address": address,
		"key": os.getenv("GOOGLE_MAPS_API_KEY")
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

# VIEWS
def index(request):
	return render(request, "index.html")

def report(request, id=None):
	if request.method == "POST":
		if not id:
			c = Case(id=Case.short_uuid())
		else:
			c = Case.objects.get(id=id)
		c.animal = request.POST.get("animal-type")
		
		# Parse coordinates from the form
		report_coords = request.POST.get("coordinates").split(",")
		report_lon, report_lat = map(float, report_coords)

		# Find users within travel distance
		nearby_users = []
		for user in User.objects.all():
			if user.home_coordinates:
				user_coords = user.home_coordinates.split(",")
				user_lat, user_lon = map(float, user_coords)
				distance = haversine(report_lon, report_lat, user_lon, user_lat)
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
			"reported",
			messages_sent,
		)
		c.save()
		print(f"New {c.animal} case saved")

		# TODO
		# Text the nearby users with a request to pickup
		# and the URL for the case page 
		client = Client(TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN)
		# Message to be sent
		message_body = f"A new {c.animal} case has been reported. Please check the details at <URL_for_case_page>"

		for phone_number in nearby_users:
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
		log_type = "Relay"
		return render(request, 'report.html', {'case':c, 'log_type':log_type})

	return render(request, 'report.html')

def map_view(request):
	cases = Case.objects.all().order_by("-created_on")
	map_data = [
		{"coordinates" : case.log[0]['coordinates'], 
		"status" : case.log[0]['status'], 
		"Animals" : case.animal,
		}
	for case in cases]
	print(map_data)
	return render(request, 'map.html', {"cases":cases, "map_data":json.dumps(map_data)})

def log(request):
	cases = Case.objects.all()
	return render(request, 'log.html', {'cases':cases})

def case(request, id):
	tt_key = os.getenv("TT_KEY")
	case = Case.objects.get(pk=id)
	coordinates = [float(c) for c in case.log[0]['coordinates']]
	if request.method == "POST":
		user_field = request.POST.get("name-confirm")
		if user_field == request.user.username:
			print(request.user)
			# Add log entry
			case.add_log_entry(
				name=request.user.first_name,
				contact_number=request.user.mobile_phone,  # Assuming contact number is stored in user profile
				message="Pickup confirmed",
				coordinates=coordinates,  # Provide the appropriate coordinates here
				status="waiting",
				messages_sent=1 #indicate one text was sent as 1 volunteer has accepted
			)
			messages.success(request, "Pickup confirmed.")
		else:
			messages.error(request, "Invalid username entered.")

	map_data = [
		{"Coordinates": coordinates,
		 "Status": case.log[0]['status'],
		 "Animal": case.animal,
		 }
	]

	return render(request, 'case.html', 
				  {"case": case, "tt_key": tt_key, "map_data": map_data})

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
	return render(request, 'register.html', {'form': form})
