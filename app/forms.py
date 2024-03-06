from django import forms  
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms.widgets import TextInput, EmailInput, PasswordInput, NumberInput, Select
from address.forms import AddressField

from app.models import User

class BaseUserCreationForm(UserCreationForm):
	def __init__(self, *args, **kwargs):
		super(BaseUserCreationForm, self).__init__(*args, **kwargs)

		# Define choices for interests
		self.fields['interests'] = forms.ChoiceField(
			choices=[
				('Dispatch', 'Dispatch (including triage centers)'),
				('Animal Care', 'Animal Care (on-site only)'),
				('Education', 'Education'),
				('Administration', 'Administration'),
				('Gardening', 'Gardening (on-site only)'),
				('Intern', 'Intern'),
			],
			widget=Select(attrs={'class': 'form-control'}),
			required=True
		)

		# Define choices for travel_distance
		self.fields['travel_distance'] = forms.ChoiceField(
			choices=[
				(50, '50KM'),
				(100, '100KM'),
				(150, '150KM'),
				(200, '200KM'),
				(250, '250KM'),
				(350, '350KM'),
				(450, '450KM'),
				(2000, 'All'),
			],
			widget=Select(attrs={'class': 'form-control'}),
			required=True
		)

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
		attrs={'placeholder': 'Home Address', 'class': 'form-control', 'id':'address-input'}),
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
				  'mobile_phone', 'home_address', 'interests', 'travel_distance',
				  'password1', 'password2']

class UserLoginForm(AuthenticationForm):
	def __init__(self,*args, **kwargs):
		super(UserLoginForm, self).__init__(*args,**kwargs)

	username = forms.CharField(widget=EmailInput(
		attrs={'placeholder':'email@domain.com','id':'email', 'class':'w-50'}))
	password = forms.CharField(widget=PasswordInput(
		attrs={'placeholder':'password','id':'password', 'class':'w-50'}))

class SetPasswordForm(forms.Form):
	password1 = forms.CharField(label='New password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='New password confirmation', widget=forms.PasswordInput)

	def clean(self):
		cleaned_data = super().clean()
		password1 = cleaned_data.get("password1")
		password2 = cleaned_data.get("password2")

		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords don't match")

		return cleaned_data