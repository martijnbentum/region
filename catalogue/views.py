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
from .forms import periodicalpublication_formset, TextTypeForm
from .forms import textreviewpublication_formset
from .forms import publicationreviewedbytext_formset,illustrationillustration_formset
from .forms import illustrationillustration_formsetr, IllustrationTypeForm
from .forms import IllustrationIllustrationRelationTypeForm
from persons.models import Person, PersonLocationRelation
from persons.forms import textperson_formset, illustrationperson_formset
from persons.forms import periodicalperson_formset
from utils import view_util, model_util
from utils.view_util import Crud, Cruds, make_tabs, FormsetFactoryManager
from utilities.views import add_simple_model, edit_model, getfocus, delete_model
from utilities.views import list_view
import os

def home(request):
    image_urls  = model_util.get_random_image_urls(n=3)
    args = {'image_urls':image_urls}
    return render(request,'catalogue/home.html',args)

def acknowledgements(request):
    args = {}
    return render(request,'catalogue/acknowledgements.html',args)


def detail_illustration(request,pk):
	illustration = Illustration.objects.get(pk = pk)
	var = {'page_name':illustration.caption}
	var.update({'instance':illustration})
	return render(request,'catalogue/d_illustration.html',var)

def detail_publication(request,pk):
	publication = Publication.objects.get(pk = pk)
	var = {'page_name':publication.title}
	var.update({'instance':publication})
	return render(request,'catalogue/d_publication.html',var)

def detail_periodical(request,pk):
	periodical= Periodical.objects.get(pk = pk)
	var = {'page_name':periodical.title}
	var.update({'instance':periodical})
	return render(request,'catalogue/d_periodical.html',var)

def detail_publisher(request,pk):
	publisher= Publisher.objects.get(pk = pk)
	var = {'page_name':publisher.name}
	var.update({'instance':publisher})
	return render(request,'catalogue/d_publisher.html',var)

def detail_text(request,pk):
	text= Text.objects.get(pk = pk)
	var = {'page_name':text.title}
	var.update({'instance':text})
	return render(request,'catalogue/d_text.html',var)

def text_list(request):
	'''list view of text.'''
	return list_view(request, 'Text', 'catalogue')


def make_fname(name):
	'''changes capitalized class names to underscore separated names.'''
	o = name[0]
	for c in name[1:]:
		if c.isupper(): o += '_' + c
		else: o += c
	return o.lower()


def create_simple_view(name):
	'''creates a simple view based on the model name
	Assumes the form only has a name field.
	'''
	c = 'def add_'+make_fname(name)+'(request,pk=None):\n'
	c += '\treturn add_simple_model(request,__name__,"'+name+'","catalogue","add '+name+'",pk=pk)'
	return exec(c,globals())

names = 'Genre,TextType,CopyRight,IllustrationCategory,PublicationType'
names += ',TextTextRelationType,IllustrationIllustrationRelationType'
names += ',IllustrationType'
for name in names.split(','):
	create_simple_view(name)


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
	names += ',illustrationillustration_formset,illustrationillustration_formsetr'
	return edit_model(request, __name__, 'Illustration', 'catalogue', pk, 
		formset_names=names, focus = focus, view=view)


def delete(request, pk, model_name):
	return delete_model(request, __name__,model_name,'catalogue',pk)

		


def ajax_test(request):
	cpu = os.popen('top -l 1 | grep -E "^CPU|^Phys"').read()
	cpu = cpu.split(',')
	data = {'hello_world':'goodbye','cpu':cpu}
	return JsonResponse(data)


# Create your views here.
