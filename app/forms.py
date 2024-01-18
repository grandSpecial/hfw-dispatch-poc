from django import forms  
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms.widgets import TextInput, EmailInput, PasswordInput, NumberInput
from address.forms import AddressField

from app.models import User

class BaseUserCreationForm(UserCreationForm):
	def __init__(self,*args, **kwargs):
		super(BaseUserCreationForm, self).__init__(*args,**kwargs)

	first_name = forms.CharField(widget=TextInput(
		attrs={'placeholder':'First Name','class':'w-50'}),
		max_length=25, required=True, label='')

	last_name = forms.CharField(widget=TextInput(
		attrs={'placeholder':'Last Name','class':'w-50'}),
		max_length=25, required=True, label='')

	username = forms.CharField(widget=EmailInput(
		attrs={'class':'w-50', 'placeholder':'Email',
		'id':'username', 'name':'username'}), label='', required=True)

	mobile_phone = forms.CharField(widget=TextInput(
		attrs={'placeholder':'Mobile Phone Number', 'class':'w-50',
		'id':'mobile_phone'}), max_length=15, required=True, label='')

	home_address = AddressField(widget=TextInput(
		attrs={'placeholder':'Home Address','class':'w-50'}),
		required=True, label='')

	travel_distance = forms.IntegerField(widget=NumberInput(
		attrs={'placeholder':100,'class':'w-50'}),
		required=True, label='')

	password1 = forms.CharField(widget=PasswordInput(
		attrs={'placeholder':'Password','class':'w-50'}), 
		label='', required=True)

	password2 = forms.CharField(widget=PasswordInput(
		attrs={'placeholder':'Confirm Password','class':'w-50'}), 
		label='', required=True)

	class Meta:
		model = User
		fields = ['first_name','last_name','username',
		'mobile_phone','home_address','travel_distance',
		'password1','password2']

class UserLoginForm(AuthenticationForm):
	def __init__(self,*args, **kwargs):
		super(UserLoginForm, self).__init__(*args,**kwargs)

	username = forms.CharField(widget=EmailInput(
		attrs={'placeholder':'email@domain.com','id':'email', 'class':'w-50'}))
	password = forms.CharField(widget=PasswordInput(
		attrs={'placeholder':'password','id':'password', 'class':'w-50'}))