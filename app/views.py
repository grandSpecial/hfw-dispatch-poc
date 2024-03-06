from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from twilio.rest import Client
import os
import requests
import os
import json
import re
from datetime import timedelta  
from dotenv import load_dotenv
load_dotenv()

from app.models import Case, User
from app.forms import BaseUserCreationForm, SetPasswordForm
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
	# filter cases by logged in user's travel_distance
	user = request.user  
	user_coords = user.home_coordinates.split(",")
	user_lat, user_lon = map(float, user_coords)
	# Only show the last 30 days of cases 
	now = timezone.now()
	date_30_days_ago = now - timedelta(days=30)
	cases = Case.objects.filter(created_on__gte=date_30_days_ago).order_by("-created_on")
	print(len(cases))
	map_data = []
	for case in cases:
		print(case.log)
		report_coords = case.log[-1]['coordinates']
		report_lat,report_lon = map(float, report_coords)
		distance = haversine(report_lon, report_lat, user_lon, user_lat)
		if distance <= user.travel_distance:
			map_data.append(
				{"id": case.id,
				"coordinates" : case.log[-1]['coordinates'], 
				"status" : case.log[-1]['status'], 
				"Animals" : case.animal,
				}
			)
	# logged in, dispatch users 
	# render all logged in users on the desktop map
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

def forgot_password(request):
    if request.method == 'POST':
        mobile_phone = request.POST.get('mobile_phone')
        phone_number = clean_number(str(mobile_phone))
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        #lookup user with mobile number
        user = User.objects.get(mobile_phone=mobile_phone)
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        # Generate a link to the password reset page with the token
        password_reset_link = f'https://hfw.tbat.io/set-password/{uidb64}/{token}'
        
        message_body = f"Please reset the password for user {user.username} by visiting: {password_reset_link}."
        message = client.messages.create(
            to=phone_number,
            from_=TWILIO_PHONE_NUMBER,
            body=message_body
        )

    return render(request, "forgot_password.html")

def set_password(request, uidb64, token):
    try:
        # Decode the user's ID from the uidb64
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['password1']
                user.set_password(new_password)
                user.save()
                print("Password has been set successfully.")
                return redirect('login')
            else:
            	print("not valid")

        else:
            form = SetPasswordForm()
    else:
        messages.error(request, 'The password reset link is invalid or has expired.')
        return redirect('login')  # Or some error page

    return render(request, 'set_password.html', {'form': form})