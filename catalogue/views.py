from django.apps import apps
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
from .models import Publication, Publisher, Text
from .forms import TextForm, PublicationForm, PublisherForm
import json
from locations.models import UserLoc
from persons.models import Person, PersonLocationRelation
from utilities.models import Date
from utils import view_util
from django.contrib.auth.decorators import login_required

@login_required
def _edit_model(request, instance_id, model_name):
	'''edit view generalized over models.
	assumes a 'add_{{model_name}}.html template and edit_{{model_name}} function
	and {{model_name}}Form
	'''
	model = apps.get_model('catalogue',model_name)
	modelform = view_util.get_modelform(__name__,model_name+'Form')
	instance= model.objects.get(pk=instance_id)
	if request.method == 'POST':
		form = modelform(request.POST, instance=instance)
		if form.is_valid():
			print('form is valid: ',form.cleaned_data,type(form))
			form.save()
			return HttpResponseRedirect(
				reverse('catalogue:'+model_name.lower()+'_list'))
	form = modelform(instance=instance)
	args = {'form':form,'page_name':'Edit '+model_name.lower()}
	return render(request,'catalogue/add_' + model_name.lower() + '.html',args)


class TextView(generic.ListView):
	template_name = 'catalogue/text_list.html'
	context_object_name = 'text_list'
	# paginate_by = 10 # http://127.0.0.1:8000/catalogue/text/?page=2
	extra_context={'page_name':'Text'}

	def get_queryset(self):
		return Text.objects.order_by('title')

class PublicationView(generic.ListView):
	template_name = 'catalogue/publication_list.html'
	context_object_name = 'publication_list'
	extra_context={'page_name':'Publication'}

	def get_queryset(self):
		return Publication.objects.order_by('title')

class PublisherView(generic.ListView):
	template_name = 'catalogue/publisher_list.html'
	context_object_name = 'publisher_list'
	extra_context={'page_name':'Publisher'}

	def get_queryset(self):
		return Publisher.objects.order_by('name')


def add_text(request):
	# if this is a post request we need to process the form data
	if request.method == 'POST':
		form = TextForm(request.POST)
		if form.is_valid():
			print('form is valid: ',form.cleaned_data,type(form))
			form.save()
			return HttpResponseRedirect('/catalogue/text/')
	form = TextForm()
	var = {'form':form,'page_name':'Add text'}
	return render(request, 'catalogue/add_text.html', var)



def add_publication(request):
	# if this is a post request we need to process the form data
	if request.method == 'POST':
		form = PublicationForm(request.POST)
		if form.is_valid():
			print('form is valid: ',form.cleaned_data,type(form))
			form.save()
			return HttpResponseRedirect('/catalogue/publication/')
	form = PublicationForm()
	var = {'form':form,'page_name':'Add Publication'}
	return render(request, 'catalogue/add_publication.html', var)



def add_publisher(request):
	# if this is a post request we need to process the form data
	if request.method == 'POST':
		form = PublisherForm(request.POST)
		if form.is_valid():
			print('form is valid: ',form.cleaned_data,type(form))
			form.save()
			return HttpResponseRedirect('/catalogue/publisher/')
	form = PublisherForm()
	var = {'form':form,'page_name':'Add Publisher'}
	return render(request, 'catalogue/add_publisher.html', var)


def edit_text(request, pk):
	return _edit_model(request, pk, 'Text')

def edit_publisher(request, pk):
	return _edit_model(request, pk, 'Publisher')

def edit_publication(request, pk):
	return _edit_model(request, pk, 'Publication')





# Create your views here.
