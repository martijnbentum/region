from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
from .models import Publication, Publisher, Text, Illustration, Periodical
from .forms import TextForm, PublicationForm, PublisherForm, PeriodicalForm
from .forms import IllustrationForm, IllustrationCategoryForm
from .forms import TextTextRelationTypeForm
from .forms import publicationtext_formset, publicationillustration_formset
from .forms import textpublication_formset, illustrationpublication_formset
from .forms import texttext_formset, texttextr_formset, publicationperiodical_formset
from .forms import periodicalpublication_formset
from locations.models import UserLoc
from persons.models import Person, PersonLocationRelation
from persons.forms import textperson_formset, illustrationperson_formset, periodicalperson_formset
from utils import view_util
from utils.view_util import Crud, Cruds, make_tabs, FormsetFactoryManager
from utilities.views import add_simple_model, edit_model, getfocus, delete_model



class PeriodicalView(generic.ListView):
	'''list view of periodicals.'''
	template_name = 'catalogue/periodical_list.html'
	context_object_name = 'periodical_list'
	# paginate_by = 10 # http://127.0.0.1:8000/catalogue/text/?page=2
	# cruds = Cruds('catalogue','Illustration')
	extra_context={'page_name':'periodical'}#,'cruds':cruds}

	def get_queryset(self):
		return Periodical.objects.order_by('title')

class IllustrationView(generic.ListView):
	'''list view of illustrations.'''
	template_name = 'catalogue/illustration_list.html'
	context_object_name = 'illustration_list'
	# paginate_by = 10 # http://127.0.0.1:8000/catalogue/text/?page=2
	# cruds = Cruds('catalogue','Illustration')
	extra_context={'page_name':'illustration'}#,'cruds':cruds}

	def get_queryset(self):
		return Illustration.objects.order_by('caption')

class TextView(generic.ListView):
	'''list view of texts.'''
	template_name = 'catalogue/text_list.html'
	context_object_name = 'text_list'
	# paginate_by = 10 # http://127.0.0.1:8000/catalogue/text/?page=2
	extra_context={'page_name':'Text'}

	def get_queryset(self):
		return Text.objects.order_by('title')

class PublicationView(generic.ListView):
	'''list view of publications.'''
	template_name = 'catalogue/publication_list.html'
	context_object_name = 'publication_list'
	extra_context={'page_name':'Publication'}

	def get_queryset(self):
		return Publication.objects.order_by('title')

class PublisherView(generic.ListView):
	'''list view of publishers.'''
	template_name = 'catalogue/publisher_list.html'
	context_object_name = 'publisher_list'
	extra_context={'page_name':'Publisher'}

	def get_queryset(self):
		return Publisher.objects.order_by('name')


def add_illustration_category(request):
	return add_simple_model(request,__name__,'IllustrationCategory','catalogue',
		'add illustration category')

def add_type(request):
	return add_simple_model(request,__name__,'PublicationType','catalogue',
		'add publication type')

def add_texttext_relation_type(request):
	return add_simple_model(request,__name__,'TextTextRelationType','catalogue',
		'text - text relation type')


def edit_text(request, pk=None, focus = '', view='complete'):
	names='texttext_formset,texttextr_formset,textperson_formset,textpublication_formset'
	return edit_model(request, __name__,'Text','catalogue',pk,formset_names=names, 
		focus = focus, view=view)

def edit_periodical(request, pk=None, focus = '', view='complete'):
	names='periodicalpublication_formset,periodicalperson_formset'
	return edit_model(request, __name__,'Periodical','catalogue', pk,formset_names=names, 
		focus = focus, view=view)

def edit_publisher(request, pk=None, focus = '', view='complete'):
	return edit_model(request, __name__,'Publisher','catalogue',pk,focus = focus, view=view)

def edit_publication(request, pk=None, focus = '', view='complete'):
	names='publicationtext_formset,publicationillustration_formset,publicationperiodical_formset'
	return edit_model(request, __name__,'Publication','catalogue',pk,
		formset_names=names, focus = focus, view=view)

def edit_illustration(request, pk=None, focus = '', view='complete'):
	names = 'illustrationperson_formset,illustrationpublication_formset'
	return edit_model(request, __name__, 'Illustration', 'catalogue', pk, 
		formset_names=names, focus = focus, view=view)


def delete(request, pk, model_name):
	return delete_model(request, __name__,model_name,'catalogue',pk)

		



# Create your views here.
