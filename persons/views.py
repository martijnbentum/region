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
from utilities.views import add_simple_model, Crud


def getnavs(request):
	'''navs are variables to set the active tabs on a page.
	navbar is the tab link
	navcontent is the content link
	'''
	navbar, navcontent = 'default', None
	if 'navbar' in request.POST.keys():
		navbar = request.POST['navbar']
	if 'navcontent' in request.POST.keys():
		navcontent= request.POST['navcontent']
	return navbar,navcontent

def listify_navs(navbar,navcontent):
	'''nav variables are csv in the url, need to transform them in a list.'''
	if ',' in navbar: navbar = navbar.split(',')
	if navcontent !=None: navcontent = navcontent.split(',')
	return navbar,navcontent
	

class PersonView(generic.ListView):
	template_name = 'persons/person_list.html'
	context_object_name = 'person_list'

	def get_queryset(self):
		return Person.objects.order_by('last_name')


def person_detail(request, person_id):
	p = Person.objects.get(pk=person_id)
	var = {'person':p,'map_name':'europe.js','location_name':'europe'}
	return render(request,'persons/person_detail.html',var)


def add_person(request):
	'''create a person instance with person location relation 
	'''
	if request.method == 'POST':
		form = PersonForm(request.POST)
		if form.is_valid():
			person = form.save()
			loc_formset = location_formset(request.POST, instance=person)
			txt_formset = text_formset(request.POST, instance=person)
			ill_formset = illustration_formset(request.POST, instance=person)
			pub_formset = publisher_formset(request.POST, instance = person)
			if loc_formset.is_valid(): loc_formset.save()
			if txt_formset.is_valid(): txt_formset.save()
			if ill_formset.is_valid(): ill_formset.save()
			if pub_formset.is_valid(): pub_formset.save()
			return HttpResponseRedirect(reverse('persons:edit_person', 
				args=[person.pk]))
	form = PersonForm()
	loc_formset = location_formset()
	txt_formset = text_formset()
	ill_formset = illustration_formset()
	pub_formset = publisher_formset()
	page_name = 'Add Person'
	var = {'form':form,'loc_formset':loc_formset,'page_name':page_name,
		'txt_formset':txt_formset,'ill_formset':ill_formset,'navbar':'default',
		'pub_formset':pub_formset}
	return render(request, 'persons/add_person.html', var)


def edit_person(request, person_id, navbar = 'default',navcontent=None):
	'''edit person instance and person location relation
	navbar and navcontent set the active tab (last used one)
	'''
	form, loc_formset, txt_formset, ill_formset = None, None, None, None
	pub_formset = None
	person = Person.objects.get(pk=person_id)
	if request.method == 'POST':
		navbar, navcontent = getnavs(request)
		form = PersonForm(request.POST,instance=person)
		if form.is_valid(): 
			person = form.save()
			loc_formset = location_formset(request.POST,instance=person)
			txt_formset = text_formset(request.POST,instance=person)
			ill_formset = illustration_formset(request.POST,instance=person)
			pub_formset = publisher_formset(request.POST, instance = person)
			if loc_formset.is_valid():
				loc_formset.save()
			if txt_formset.is_valid():
				txt_formset.save()
			if ill_formset.is_valid():
				ill_formset.save()
			if pub_formset.is_valid():
				pub_formset.save()
			return HttpResponseRedirect(reverse('persons:edit_person', 
				args = [person.pk, navbar, navcontent]))
		else:  print('form invalid', form.errors)
	if loc_formset ==None:loc_formset = location_formset(instance=person)
	if form == None: form = PersonForm(instance=person)
	if txt_formset == None:txt_formset = text_formset(instance=person)
	if ill_formset == None:ill_formset = illustration_formset(instance=person)
	if pub_formset == None:pub_formset = publisher_formset(instance=person)
	page_name = 'Edit Person'
	navbar,navcontent = listify_navs(navbar,navcontent)
	crud = Crud(person)
	var = {'form':form,'loc_formset':loc_formset,'page_name':page_name,
		'txt_formset':txt_formset,'ill_formset':ill_formset,
		'navbar':navbar, 'navcontent':navcontent,'pub_formset':pub_formset,
		'crud':crud}
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
