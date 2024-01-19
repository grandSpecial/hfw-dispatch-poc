from django import forms  
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms.widgets import TextInput, EmailInput, PasswordInput, NumberInput
from address.forms import AddressField

from app.models import User

class BaseUserCreationForm(UserCreationForm):
	def __init__(self, *args, **kwargs):
		super(BaseUserCreationForm, self).__init__(*args, **kwargs)

	first_name = forms.CharField(widget=TextInput(
		attrs={'placeholder': 'First Name', 'class': 'form-control'}),
		max_length=25, required=True)

	last_name = forms.CharField(widget=TextInput(
		attrs={'placeholder': 'Last Name', 'class': 'form-control'}),
		max_length=25, required=True)

	username = forms.CharField(widget=EmailInput(
		attrs={'class': 'form-control', 'placeholder': 'Email'}),
		required=True)

	mobile_phone = forms.CharField(widget=TextInput(
		attrs={'placeholder': 'Mobile Phone Number', 
		'class': 'form-control', 'id': 'mobile_phone'}),
		max_length=15, required=True)

	home_address = forms.CharField(widget=TextInput(
		attrs={'placeholder': 'Home Address', 'class': 'form-control'}),
		required=True)

	travel_distance = forms.IntegerField(widget=NumberInput(
		attrs={'placeholder': 'Maximum travel distance from home', 'class': 'form-control'}),
		required=True)

	password1 = forms.CharField(widget=PasswordInput(
		attrs={'placeholder': 'Password', 'class': 'form-control'}), 
		required=True)

	password2 = forms.CharField(widget=PasswordInput(
		attrs={'placeholder': 'Confirm Password', 'class': 'form-control'}), 
		required=True)

	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'username',
				  'mobile_phone', 'home_address', 'travel_distance',
				  'password1', 'password2']

class UserLoginForm(AuthenticationForm):
	def __init__(self,*args, **kwargs):
		super(UserLoginForm, self).__init__(*args,**kwargs)

	username = forms.CharField(widget=EmailInput(
		attrs={'placeholder':'email@domain.com','id':'email', 'class':'w-50'}))
	password = forms.CharField(widget=PasswordInput(
		attrs={'placeholder':'password','id':'password', 'class':'w-50'}))