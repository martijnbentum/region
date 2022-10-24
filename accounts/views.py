from django.shortcuts import render
from django.contrib.auth.models import User 
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.views import generic
from . forms import RegisterForm, EditProfileForm
from utils.view_util import Crud

def index(request):
	return render(request, 'registration/login.html')
# Create your views here.

class PasswordsChangeView(PasswordChangeView):
	form_class = PasswordChangeForm
	success_url = reverse_lazy('catalogue:text_view')
	template_name = 'accounts/change_password.html'

class RegisterView(generic.CreateView):
	form_class = RegisterForm
	success_url = reverse_lazy('login')
	template_name = 'accounts/register.html'

class UserEditView(generic.UpdateView):
	form_class = EditProfileForm 
	success_url = reverse_lazy('catalogue:text_view')
	template_name = 'accounts/edit_profile.html'

	def get_object(self):
		return self.request.user

def created_by_me_view(request):
	'''create a list of all update events performed by a particular user.'''
	user = User.objects.get(username = request.user.username)
	crud = Crud(user,user=True) 
	nitems= len(crud.all_created_instances)
	var = {'crud':crud,'page_name':'Created by me','nitems':nitems}
	return render(request,'accounts/created_by_me.html',var)

def log_view(request):
	'''create a list of all update events performed by a particular user.'''
	user = User.objects.get(username = request.user.username)
	crud = Crud(user,user=True) 
	nedits = len(crud.events)
	var = {'crud':crud,'page_name':'logs','nedits':nedits}
	return render(request,'accounts/log.html',var)

def logs_view(request):
	'''create a list of all update events of all users.'''
	users = User.objects.all()
	cruds = [Crud(user,user=True) for user in users]
	events = []
	for crud in cruds:
		events.extend(crud.events)
	events = sorted(events, reverse=True)
	#create placeholder to hold all events and create updates_str
	crud = Crud(users[0],user=True) 
	crud.events = events
	nedits = len(events)
	var = {'cruds':cruds,'page_name':'logs','updates':crud.updates_str}
	var.update({'nedits':nedits})
	return render(request,'accounts/logs.html',var)
