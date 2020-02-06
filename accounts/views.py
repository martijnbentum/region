from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from . forms import RegisterForm

def index(request):
	return render(request, 'registration/login.html')
# Create your views here.

class RegisterView(generic.CreateView):
	form_class = RegisterForm
	success_url = reverse_lazy('login')
	template_name = 'accounts/register.html'

