from django import forms  
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms.widgets import TextInput, EmailInput, PasswordInput
from app.models import User

class BaseUserCreationForm(UserCreationForm):
	def __init__(self,*args, **kwargs):
		super(BaseUserCreationForm, self).__init__(*args,**kwargs)

	first_name = forms.CharField(widget=TextInput(
		attrs={'placeholder':'First Name','class':'w-50'}),
		max_length=25, required=False, label='')

	last_name = forms.CharField(widget=TextInput(
		attrs={'placeholder':'Last Name','class':'w-50'}),
		max_length=25, required=False, label='')

	username = forms.CharField(widget=EmailInput(
		attrs={'class':'w-50', 'placeholder':'Email',
		'id':'username', 'name':'username'}), label='', required=False)
		#'pattern':"[a-z.]*[@]\bsaltwire.com"

	password1 = forms.CharField(widget=PasswordInput(
		attrs={'placeholder':'Password','class':'w-50'}), label='', required=False)

	password2 = forms.CharField(widget=PasswordInput(
		attrs={'placeholder':'Confirm Password','class':'w-50'}), label='', required=False)

	class Meta:
		model = User
		fields = ['first_name','last_name','username','password1','password2']

class UserLoginForm(AuthenticationForm):
	def __init__(self,*args, **kwargs):
		super(UserLoginForm, self).__init__(*args,**kwargs)

	username = forms.CharField(widget=EmailInput(
		attrs={'placeholder':'email@domain.com','id':'email', 'class':'w-50'}))
	password = forms.CharField(widget=PasswordInput(
		attrs={'placeholder':'password','id':'password', 'class':'w-50'}))