from django.apps import apps
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
# from utilities.models import Date 
from .models import Person, PersonLocationRelation, LocationRelation, Movement, MovementType
from .forms import PersonForm, PersonLocationRelationForm, LocationRelationForm
from .forms import location_formset, persontext_formset, personillustration_formset
from .forms import personpublisher_formset, PseudonymForm, MovementForm
from .forms import PersonTextRelationRoleForm, PersonIllustrationRelationRoleForm
from .forms import movementperson_formset, personmovement_formset
from .forms import PersonMovementRelationRoleForm, MovementTypeForm
from .forms import personperson_formset, personpersonr_formset, PersonPersonRelationTypeForm
from .forms import PersonPeriodicalRelationRoleForm, personperiodical_formset
from django.forms import inlineformset_factory
import json
from locations.models import UserLoc
from utils import view_util
from utils.view_util import Crud, make_tabs, get_modelform, FormsetFactoryManager
from utilities.views import add_simple_model, getfocus, edit_model, delete_model
	

class PersonView(generic.ListView):
	template_name = 'persons/person_list.html'
	context_object_name = 'person_list'

	def get_queryset(self):
		return Person.objects.order_by('last_name')


class MovementView(generic.ListView):
	template_name = 'persons/movement_list.html'
	context_object_name = 'movement_list'

	def get_queryset(self):
		return Movement.objects.order_by('name')


def person_detail(request, person_id):
	p = Person.objects.get(pk=person_id)
	var = {'person':p,'map_name':'europe.js','location_name':'europe'}
	return render(request,'persons/person_detail.html',var)


def add_person_person_relation_type(request):
	return add_simple_model(request,__name__,'PersonPersonRelationType',
		'persons','person - person relation type')

def add_person_location_relation(request):
	return add_simple_model(request,__name__,'LocationRelation','persons',
		'person - location relation')

def add_person_text_relation_role(request):
	return add_simple_model(request,__name__,'PersonTextRelationRole','persons',
		'person - text relation role')

def add_person_illustration_relation_role(request):
	return add_simple_model(request,__name__,'PersonIllustrationRelationRole',
		'persons','person - illustration relation role')

def add_person_movement_relation_role(request):
	return add_simple_model(request,__name__,'PersonMovementRelationRole',
		'persons','person - movement relation role')

def add_person_periodical_relation_role(request):
	return add_simple_model(request,__name__,'PersonPeriodicalRelationRole',
		'persons','person - periodical relation role')

def add_movement_type(request):
	return add_simple_model(request,__name__,'MovementType',
		'persons','movement type')

def add_pseudonym(request):
	return add_simple_model(request,__name__,'Pseudonym',
		'persons','add pseudonym')
		
		
def edit_person(request, pk=None, focus = '', view='complete'):
	'''add or edit a person instance and person location relation
	navbar and navcontent set the active tab (last used one)
	'''
	names='location_formset,persontext_formset,personillustration_formset'
	names+=',personmovement_formset,personpublisher_formset,personperson_formset'
	names+=',personpersonr_formset,personperiodical_formset'
	return edit_model(request, __name__, 'Person', 'persons', pk, 
		formset_names=names, focus = focus, view=view)


def edit_movement(request, pk=None, focus = '', view='complete'):
	'''add or edit a movement instance.'''
	names='movementperson_formset'
	return edit_model(request, __name__, 'Movement', 'persons', pk, 
		formset_names=names, focus = focus, view=view)


def delete(request, pk, model_name):
	return delete_model(request, __name__,model_name,'persons',pk)
