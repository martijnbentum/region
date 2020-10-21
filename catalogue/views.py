from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models.functions import Lower
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
from .models import Publication, Publisher, Text, Illustration, Periodical
from .forms import TextForm, PublicationForm, PublisherForm, PeriodicalForm
from .forms import IllustrationForm, IllustrationCategoryForm
from .forms import TextTextRelationTypeForm, CopyRightForm, GenreForm
from .forms import publicationtext_formset, publicationillustration_formset
from .forms import textpublication_formset, illustrationpublication_formset
from .forms import texttext_formset, texttextr_formset, publicationperiodical_formset
from .forms import periodicalpublication_formset, TextTypeForm, textreviewpublication_formset
from .forms import publicationreviewedbytext_formset
from persons.models import Person, PersonLocationRelation
from persons.forms import textperson_formset, illustrationperson_formset, periodicalperson_formset
from utils import view_util
from utils.view_util import Crud, Cruds, make_tabs, FormsetFactoryManager
from utilities.views import add_simple_model, edit_model, getfocus, delete_model,list_view
import os


'''
class PeriodicalView(generic.ListView):
	template_name = 'catalogue/periodical_list.html'
	context_object_name = 'periodical_list'
	# paginate_by = 10 # http://127.0.0.1:8000/catalogue/text/?page=2
	# cruds = Cruds('catalogue','Illustration')
	extra_context={'page_name':'periodical'}#,'cruds':cruds}

	def get_queryset(self):
		return Periodical.objects.order_by('title')
'''

def text_list(request):
	'''list view of text.'''
	return list_view(request, 'Text', 'catalogue')

def publication_list(request):
	'''list view of publications.'''
	return list_view(request, 'Publication', 'catalogue')

def publisher_list(request):
	'''list view of publishers.'''
	return list_view(request, 'Publisher', 'catalogue')

def periodical_list(request):
	'''list view of periodicals.'''
	return list_view(request, 'Periodical', 'catalogue')

def illustration_list(request):
	'''list view of illustrations.'''
	return list_view(request, 'Illustration', 'catalogue')



def add_genre(request):
	return add_simple_model(request,__name__,'Genre','catalogue',
		'add genre')

def add_text_type(request):
	return add_simple_model(request,__name__,'TextType','catalogue',
		'add text type')

def add_copy_right(request):
	return add_simple_model(request,__name__,'CopyRight','catalogue',
		'add license')

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
	names+=',textreviewpublication_formset'
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
	names+=',publicationreviewedbytext_formset'

	return edit_model(request, __name__,'Publication','catalogue',pk,
		formset_names=names, focus = focus, view=view)

def edit_illustration(request, pk=None, focus = '', view='complete'):
	names = 'illustrationperson_formset,illustrationpublication_formset'
	return edit_model(request, __name__, 'Illustration', 'catalogue', pk, 
		formset_names=names, focus = focus, view=view)


def delete(request, pk, model_name):
	return delete_model(request, __name__,model_name,'catalogue',pk)

		

def hello_world(request):
	return render(request, 'catalogue/hello_world.html')

def ajax_test(request):
	cpu = os.popen('top -l 1 | grep -E "^CPU|^Phys"').read()
	cpu = cpu.split(',')
	data = {'hello_world':'goodbye','cpu':cpu}
	return JsonResponse(data)


# Create your views here.
