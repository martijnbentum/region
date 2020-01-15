from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
from .models import Date, Person, Text,PersonLocationRelation
from .forms import PersonForm, TextForm, PersonLocationRelationForm
from .forms import location_formset 
from django.forms import inlineformset_factory
import json
from locations.models import UserLoc

		

class TextView(generic.ListView):
	template_name = 'catalogue/text_list.html'
	context_object_name = 'text_list'

	def get_queryset(self):
		return Text.objects.order_by('title')


def add_text(request):
	# if this is a post request we need to process the form data
	if request.method == 'POST':
		form = PersonForm(request.POST)
		if form.is_valid():
			print('form is valid: ',form.cleaned_data,type(form))
			form.save()
			return HttpResponseRedirect('/text/')
	else:
		form = TextForm()
	var = {'form':form,'page_name':'Add text'}
	return render(request, 'catalogue/add_text.html', var)


class PersonView(generic.ListView):
	template_name = 'catalogue/person_list.html'
	context_object_name = 'person_list'

	def get_queryset(self):
		return Person.objects.order_by('last_name')


def person_detail(request, person_id):
	p = Person.objects.get(pk=person_id)
	# form = PersonForm(instance=p)
	# print(form.instance.view())
	var = {'person':p}
	return render(request,'catalogue/add_person.html',{'form':form})



def _handle_date(goal_object,form,names=None):
	if names == None: 
		names = 'date,start_date,end_date,start_spec,end_spec'
	date_name,start_date,end_date,start_spec,end_spec = names.split(',')
	f = form
	try: date = getattr(goal_object,date_name)
	except: date = None
	if date == None:
		d = Date(start=f[start_date],end=f[end_date],
			start_specificity=f[start_spec],
			end_specificity=f[end_spec])
		d.save()
		setattr(goal_object,date_name,d)
	else:
		date.start = f[start_date]
		date.end = f[end_date]
		date.start_specificity = f[start_spec]
		date.end_specificity = f[end_spec]
		date.save()
	goal_object.save()
	# print(goal_object.view())


def _handle_plr_formset(formset):
	'''handle inline formset for personlocation relation'''
	plrs = formset.save(commit = False)
	for f,plr in zip(formset.cleaned_data,plrs):
		if f['DELETE']: continue
		if not f['location']: continue
		_handle_date(plr,f)
	[obj.delete() for obj in formset.deleted_objects]


def _handle_person_form(form):
	'''create or edit person instance 
	date is an object and needs to be created seperately 
	handle date object creation and saving
	'''
	f = form.cleaned_data
	person= form.save()
	names = 'birth_death_date,date_of_birth,date_of_death,birth_spec,death_spec'
	_handle_date(person,f,names=names)
	return person
	

def add_person(request):
	'''create a person instance from person form
	a date and a personlocationrelation object might need to be created
	this leads to more involved form handling
	'''
	if request.method == 'POST':
		form = PersonForm(request.POST)
		if form.is_valid():
			person = _handle_person_form(form)
			formset = location_formset(request.POST, 
				request.FILES, instance=person)
			if formset.is_valid():
				_handle_plr_formset(formset)
				return HttpResponseRedirect(reverse('catalogue:edit_person', 
					args=[person.pk]))
	form = PersonForm()
	formset = location_formset()
	page_name = 'Add Person'
	var = {'form':form,'formset':formset,'page_name':page_name}
	return render(request, 'catalogue/add_person.html', var)

def _populate_personform(person):
	'''populate personform with pre existing data.'''
	form = PersonForm(instance=person)
	sd, ed = form.fields['date_of_birth'], form.fields['date_of_death']
	ss, es = form.fields['birth_spec'], form.fields['death_spec']
	bdd = form.instance.birth_death_date
	if bdd: 
		sd.widget.attrs['value'] = sd.clean(bdd.start)
		ed.widget.attrs['value'] = ed.clean(bdd.end)
		ss.initial = bdd.start_specificity
		es.initial = bdd.end_specificity
	
	formset = location_formset(instance=person)
	for f in formset.initial_forms:
		sd, ed= f.fields['start_date'], f.fields['end_date']
		if f.instance.date:
			isd, ied = f.instance.date.start, f.instance.date.end
			sd.widget.attrs['value'] = sd.clean(isd)
			ed.widget.attrs['value']= ed.clean(ied)

			ss, es= f.fields['start_spec'], f.fields['end_spec']
			iss = f.instance.date.start_specificity
			ies = f.instance.date.end_specificity
			ss.initial = ss.clean(iss)
			es.initial = es.clean(ies)
	return form, formset

def edit_person(request, person_id):
	'''edit person instance
	form does not follow person model therefore more involved form and formset
	handling is needed
	'''
	person = Person.objects.get(pk=person_id)
	if request.method == 'POST':
		formset = location_formset(request.POST, request.FILES, instance=person)
		form = PersonForm(request.POST,instance=person)
		if form.is_valid() and formset.is_valid():
			person = _handle_person_form(form)
			_handle_plr_formset(formset)
			return HttpResponseRedirect(reverse('catalogue:edit_person', 
				args = [person.pk]))
	form, formset = _populate_personform(person)
		
	page_name = 'Edit Person'
	var = {'form':form,'formset':formset,'page_name':page_name}
	return render(request, 'catalogue/add_person.html',var)


def add_person_location_relation(request, person_id=None):
	# if this is a post request we need to process the form data
	if request.method == 'POST':
		form = PersonForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/person/')
	else:
		if person_id:
			pass
		else: 
			form = PersonLocationRelationForm()
			var = {'form':form,'page_name':'Add person location'}
	return render(request, 'catalogue/add_person_location.html', var)
	

def add_location(request):
	# if this is a post request we need to process the form data
	if request.method == 'POST':
		form = LocationForm(request.POST)
		if form.is_valid():
			print('form is valid: ',form.cleaned_data)
			form.save()
			return HttpResponseRedirect('/admin/catalogue/location/')
	else:
		form = LocationForm()
	var = {'form':form,'page_name':'Add location'}
	return render(request, 'catalogue/add_location.html', var)



# Create your views here.
