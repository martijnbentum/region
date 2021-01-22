from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User

dattr = {'attrs':{'style':'width:100%'}}
dchar = {'widget':forms.TextInput(**dattr),'required':False}
dchar_required = {'widget':forms.TextInput(**dattr),'required':True}


class RegisterForm(UserCreationForm):
	email = forms.EmailField(max_length=200, help_text='Required')
	first_name = forms.CharField(max_length=200)
	last_name = forms.CharField(max_length=200)

	class Meta:
		model = User
		fields = ('username', 'first_name','last_name',
			'email', 'password1', 'password2')

class EditProfileForm(UserChangeForm):
	email = forms.EmailField(**dchar_required)
	first_name = forms.CharField(**dchar)
	last_name = forms.CharField(**dchar)
	username= forms.CharField(**dchar)

	class Meta:
		model = User
		fields = ('username', 'first_name','last_name','email')
