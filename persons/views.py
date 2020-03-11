from django.apps import apps
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
# from utilities.models import Date 
from .models import Person, PersonLocationRelation, LocationRelation
from .forms import PersonForm, PersonLocationRelationForm, LocationRelationForm
from .forms import location_formset, text_formset, illustration_formset
from .forms import publisher_formset, PseudonymForm
from .forms import PersonTextRelationRoleForm, PersonIllustrationRelationRoleForm
from django.forms import inlineformset_factory
import json
from locations.models import UserLoc
from utils import view_util
from utils.view_util import Crud, make_tabs
from utilities.views import add_simple_model, getfocus
	

class PersonView(generic.ListView):
	template_name = 'persons/person_list.html'
	context_object_name = 'person_list'

	def get_queryset(self):
		return Person.objects.order_by('last_name')


def person_detail(request, person_id):
	p = Person.objects.get(pk=person_id)
	var = {'person':p,'map_name':'europe.js','location_name':'europe'}
	return render(request,'persons/person_detail.html',var)


def edit_person(request, person_id = None, focus = ''):
	'''add or edit a person instance and person location relation
	navbar and navcontent set the active tab (last used one)
	'''
	form, loc_formset, txt_formset, ill_formset = None, None, None, None
	pub_formset = None
	if person_id: person = Person.objects.get(pk=person_id)
	if request.method == 'POST':
		focus = getfocus(request)
		if person_id: form = PersonForm(request.POST,instance=person)
		else: form = PersonForm(request.POST)
		if form.is_valid(): 
			person = form.save()
			loc_formset = location_formset(request.POST,instance=person)
			txt_formset = text_formset(request.POST,instance=person)
			ill_formset = illustration_formset(request.POST,instance=person)
			pub_formset = publisher_formset(request.POST, instance = person)
			if loc_formset.is_valid(): loc_formset.save()
			if txt_formset.is_valid(): txt_formset.save()
			if ill_formset.is_valid(): ill_formset.save()
			if pub_formset.is_valid(): pub_formset.save()
			return HttpResponseRedirect(reverse('persons:edit_person', 
				args = [person.pk, focus]))
		else:  print('form invalid', form.errors)
	if person_id == None:
		form = PersonForm()
		loc_formset = location_formset()
		txt_formset = text_formset()
		ill_formset = illustration_formset()
		pub_formset = publisher_formset()
	else:
		if loc_formset ==None:loc_formset = location_formset(instance=person)
		if form == None: form = PersonForm(instance=person)
		if txt_formset == None:txt_formset = text_formset(instance=person)
		if ill_formset == None:
			ill_formset = illustration_formset(instance=person)
		if pub_formset == None:pub_formset = publisher_formset(instance=person)
	page_name = 'Edit Person' if person_id else 'Add Person'
	tabs = make_tabs('person',focus_names = focus)
	if person_id: crud = Crud(person)
	else: crud = None
	var = {'form':form,'loc_formset':loc_formset,'page_name':page_name,
		'txt_formset':txt_formset,'ill_formset':ill_formset,
		'tabs':tabs,'pub_formset':pub_formset,'crud':crud}
	return render(request, 'persons/add_person.html',var)


def add_person_location_relation(request):
	return add_simple_model(request,__name__,'LocationRelation','persons',
		'person - location relation')

def add_person_text_relation_role(request):
	return add_simple_model(request,__name__,'PersonTextRelationRole','persons',
		'person - text relation role')

def add_person_illustration_relation_role(request):
	return add_simple_model(request,__name__,'PersonIllustrationRelationRole',
		'persons','person - illustration relation role')

def add_pseudonym(request):
	return add_simple_model(request,__name__,'Pseudonym',
		'persons','add pseudonym')
		
		

# Create your views here.
