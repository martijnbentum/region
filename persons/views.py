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
from django.forms import inlineformset_factory
import json
from locations.models import UserLoc
from utils import view_util
from utils.view_util import Crud, make_tabs, get_modelform, FormsetFactoryManager
from utilities.views import add_simple_model, getfocus
	

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


def make_ffm(names):
	print(names,type(names))
	return FormsetFactoryManager(__name__,names)
	

def person_detail(request, person_id):
	p = Person.objects.get(pk=person_id)
	var = {'person':p,'map_name':'europe.js','location_name':'europe'}
	return render(request,'persons/person_detail.html',var)


def edit_person(request, person_id = None, focus = '', view = 'complete'):
	'''add or edit a person instance and person location relation
	navbar and navcontent set the active tab (last used one)
	'''
	names='location_formset,persontext_formset,personillustration_formset'
	names+=',personmovement_formset,personpublisher_formset'
	person = Person.objects.get(pk=person_id) if person_id else None
	ffm, form = None, None
	if request.method == 'POST':
		focus = getfocus(request)
		form = PersonForm(request.POST,instance=person)
		if form.is_valid(): 
			person = form.save()
			if view == 'inline': return HttpResponseRedirect('/utilities/close/')
			ffm = FormsetFactoryManager(__name__,names,request,person)
			valid = ffm.save()
			if valid: 
				return HttpResponseRedirect(reverse('persons:edit_person', 
					args = [person.pk, focus]))
		else:  print('form invalid', form.errors)
	if not form: form = PersonForm(instance=person)
	if not ffm: ffm = FormsetFactoryManager(__name__,names,instance=person)
	page_name = 'Edit Person' if person_id else 'Add Person'
	tabs = make_tabs('person',focus_names = focus)
	crud = Crud(person) if person_id else None
	var = {'form':form,'page_name':page_name, 'tabs':tabs,'crud':crud, 'view':view}
	var.update(ffm.dict)
	return render(request, 'persons/add_person.html',var)


def edit_movement(request, pk = None, focus = '', view = 'complete'):
	'''add or edit a movement instance 
	'''
	names='movementperson_formset'
	movement = Movement.objects.get(pk=pk) if pk else None
	ffm, form = None, None
	if request.method == 'POST':
		focus = getfocus(request)
		print(focus,99)
		form = MovementForm(request.POST,instance=movement)
		if form.is_valid(): 
			movement = form.save()
			if view == 'inline': return HttpResponseRedirect('/utilities/close/')
			ffm = FormsetFactoryManager(__name__,names,request,movement)
			valid = ffm.save()
			if valid: 
				return HttpResponseRedirect(reverse('persons:edit_movement', 
					args = [movement.pk, focus]))
		else:  print('form invalid', form.errors)
	if not form: form = MovementForm(instance=movement)
	if not ffm: ffm = FormsetFactoryManager(__name__,names,instance=movement)
	page_name = 'Edit movement' if pk else 'Add movement'
	tabs = make_tabs('movement',focus_names = focus)
	crud = Crud(movement) if pk else None
	var = {'form':form,'page_name':page_name, 'tabs':tabs,'crud':crud, 'view':view}
	var.update(ffm.dict)
	return render(request, 'persons/add_movement.html',var)


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

def add_movement_type(request):
	return add_simple_model(request,__name__,'MovementType',
		'persons','movement type')

def add_pseudonym(request):
	return add_simple_model(request,__name__,'Pseudonym',
		'persons','add pseudonym')
		
		

# Create your views here.
