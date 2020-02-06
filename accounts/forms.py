from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
	email = forms.EmailField(max_length=200, help_text='Required')
	first_name = forms.CharField(max_length=200)
	last_name = forms.CharField(max_length=200)

	class Meta:
		model = User
		fields = ('username', 'first_name','last_name',
			'email', 'password1', 'password2')
