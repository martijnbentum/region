from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
from .models import Publication, Publisher, Text, Illustration
from .forms import TextForm, PublicationForm, PublisherForm 
from .forms import IllustrationForm, IllustrationCategoryForm
from .forms import text_formset, illustration_formset, PublicationTypeForm
from .forms import texttext_formset
from locations.models import UserLoc
from persons.models import Person, PersonLocationRelation
from utils import view_util
from utils.view_util import Crud, Cruds, make_tabs, FormsetFactoryManager
from utilities.views import add_simple_model 


@login_required
def _edit_model(request, instance_id, model_name, formset_names='', focus=''):
	'''edit view generalized over models.
	assumes a 'add_{{model_name}}.html template and edit_{{model_name}} function
	and {{model_name}}Form
	'''
	names = formset_names
	model = apps.get_model('catalogue',model_name)
	modelform = view_util.get_modelform(__name__,model_name+'Form')
	instance= model.objects.get(pk=instance_id)
	crud = Crud(instance)
	ffm, form = None, None
	if request.method == 'POST':
		form = modelform(request.POST, request.FILES, instance=instance)
		if form.is_valid():
			print('form is valid: ',form.cleaned_data,type(form))
			instance = form.save()
			ffm = FormsetFactoryManager(__name__,names,request,instance)
			valid = ffm.save()
			if valid:
				return HttpResponseRedirect(reverse(
					'catalogue:edit_'+model_name.lower(), 
					args = [instance.pk]))
	if not form: form = modelform(instance=instance)
	if not ffm: ffm = FormsetFactoryManager(__name__,names,instance=instance)
	tabs = make_tabs(model_name.lower(), focus_names = focus)
	args = {'form':form,'page_name':'Edit '+model_name.lower(),'crud':crud,
		'tabs':tabs}
	args.update(ffm.dict)
	return render(request,'catalogue/add_' + model_name.lower() + '.html',args)



class IllustrationView(generic.ListView):
	template_name = 'catalogue/illustration_list.html'
	context_object_name = 'illustration_list'
	# paginate_by = 10 # http://127.0.0.1:8000/catalogue/text/?page=2
	cruds = Cruds('catalogue','Illustration')
	extra_context={'page_name':'illustration','cruds':cruds}

	def get_queryset(self):
		return Illustration.objects.order_by('caption')

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


def add_text(request, view = 'complete',focus = ''):
	# if this is a post request we need to process the form data
	ffm, form = None, None
	names='texttext_formset'
	if request.method == 'POST':
		print(request.FILES)
		form = TextForm(request.POST, request.FILES)
		if form.is_valid():
			print('form is valid: ',form.cleaned_data,type(form))
			form.save()
			if view == 'complete':
				ffm = FormsetFactoryManager(__name__,names,request,publication)
				valid = ffm.save()
				if valid:
					return httpresponseredirect('/catalogue/text/')
			else: return HttpResponseRedirect('/catalogue/close/')
	if not form: form = TextForm()
	if not ffm: ffm = FormsetFactoryManager(__name__,names)
	tabs = make_tabs('text',focus_names = focus)
	var = {'form':form,'page_name':'Add text','view':view,'tabs':tabs}
	var.update(ffm.dict)
	print(ffm.dict)
	return render(request, 'catalogue/add_text.html', var)


def add_publication(request, view='complete', focus = ''):
	# if this is a post request we need to process the form data
	names='text_formset,illustration_formset'
	ffm, form = None, None
	if request.method == 'POST':
		form = PublicationForm(request.POST, request.FILES)
		if form.is_valid():
			print('form is valid: ',form.cleaned_data,type(form))
			publication = form.save()
			if view == 'complete':
				ffm = FormsetFactoryManager(__name__,names,request,publication)
				valid = ffm.save()
				if valid:
					return HttpResponseRedirect('/catalogue/publication/')
			else: return HttpResponseRedirect('/catalogue/close/')
	if not form: form = PublicationForm()
	if not ffm: ffm = FormsetFactoryManager(__name__,names)
	tabs = make_tabs('publication',focus_names = focus)
	var = {'form':form,'page_name':'Add Publication','view':view,'tabs':tabs}
	var.update(ffm.dict)
	return render(request, 'catalogue/add_publication.html', var)


def add_publisher(request,view='complete'):
	# if this is a post request we need to process the form data
	if request.method == 'POST':
		form = PublisherForm(request.POST)
		if form.is_valid():
			print('form is valid: ',form.cleaned_data,type(form))
			form.save()
			if view == 'complete':
				return HttpResponseRedirect('/catalogue/publisher/')
			return HttpResponseRedirect('/catalogue/close/')
	form = PublisherForm()
	var = {'form':form,'page_name':'Add Publisher','view':view}
	return render(request, 'catalogue/add_publisher.html', var)


def add_illustration(request,view='complete'):
	# if this is a post request we need to process the form data
	if request.method == 'POST':
		form = IllustrationForm(request.POST, request.FILES)
		if form.is_valid():
			print('form is valid: ',form.cleaned_data,type(form))
			form.save()
			if view == 'complete':
				return HttpResponseRedirect('/catalogue/illustration/')
			return HttpResponseRedirect('/catalogue/close/')
	form = IllustrationForm()
	var = {'form':form,'page_name':'Add Illustration','view':view}
	return render(request, 'catalogue/add_illustration.html', var)


def add_illustration_category(request):
	return add_simple_model(request,__name__,'IllustrationCategory','catalogue',
		'add illustration category')

def add_type(request):
	return add_simple_model(request,__name__,'PublicationType','catalogue',
		'add publication type')

def edit_text(request, pk):
	return _edit_model(request, pk, 'Text')

def edit_publisher(request, pk):
	return _edit_model(request, pk, 'Publisher')

def edit_publication(request, pk):
	names='text_formset,illustration_formset'
	return _edit_model(request, pk, 'Publication',formset_names=names)

def edit_illustration(request, pk):
	return _edit_model(request, pk, 'Illustration')





# Create your views here.
