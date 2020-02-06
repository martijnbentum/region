from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

def index(request):
	return render(request, 'registration/login.html')
# Create your views here.

class Register(generic.CreateView):
	form_class = UserCreationForm
	succes_url = reverse_lazy('login')
	template_name = 'accounts/register.html'

