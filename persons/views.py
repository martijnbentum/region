from django.apps import apps
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
# from utilities.models import Date 
from .models import Person, PersonLocationRelation, PersonLocationRelationType, Movement 
from .models import MovementType
from .forms import PersonForm, PersonLocationRelationForm, PersonLocationRelationTypeForm
from .forms import location_formset, persontext_formset, personillustration_formset
from .forms import personpublisher_formset, PseudonymForm, MovementForm
from .forms import PersonTextRelationRoleForm, PersonIllustrationRelationRoleForm
from .forms import movementperson_formset, personmovement_formset
from .forms import PersonMovementRelationRoleForm, MovementTypeForm
from .forms import personperson_formset, personpersonr_formset 
from .forms import PersonPersonRelationTypeForm
from .forms import PersonPeriodicalRelationRoleForm, personperiodical_formset
from django.forms import inlineformset_factory
import json
from utils import view_util
from utils.view_util import Crud, make_tabs, get_modelform, FormsetFactoryManager
from utilities.views import add_simple_model, getfocus, edit_model, delete_model,list_view
	
def detail_movement(request,pk):
	movement = Movement.objects.get(pk = pk)
	var = {'page_name':movement.name}
	var.update({'instance':movement})
	return render(request,'persons/d_movement.html',var)

def detail_person(request,pk):
	person= Person.objects.get(pk = pk)
	var = {'page_name':person.name}
	var.update({'instance':person})
	return render(request,'persons/d_person.html',var)

def make_fname(name):
	'''replace capitalized letter to lower case and insert an underscore before
	except for the fort character in a string.
	'''
	o = name[0]
	for c in name[1:]:
		if c.isupper(): o += '_' + c
		else: o += c
	return o.lower()


def create_simple_view(name):
	'''creates a simple view based on the model name
	Assumes the form only has a name field.
	'''
	p_name = make_fname(name).replace('_',' ') +'aaa'
	# print(p_name,123)
	c = 'def add_'+make_fname(name)+'(request,pk=None):\n'
	c += '\treturn add_simple_model(request,__name__,"'+name+'","persons","add '+p_name+'",pk=pk)'
	return exec(c,globals())

#for each name in the list below create a simple view
names = 'PersonPersonRelationType,PersonLocationRelationType,PersonTextRelationRole'
names += ',PersonIllustrationRelationRole,PersonMovementRelationRole'
names += ',PersonPeriodicalRelationRole,MovementType,Pseudonym'
for name in names.split(','):
	create_simple_view(name)

'''


def add_person_person_relation_type(request):
	return add_simple_model(request,__name__,'PersonPersonRelationType',
		'persons','person - person relation type')

def add_person_location_relation(request):
	return add_simple_model(request,__name__,'PersonLocationRelationType','persons',
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
'''
		
		
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
