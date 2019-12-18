from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
from .models import Date, Location, Person, Text,PersonLocationRelation
from .forms import PersonForm, LocationForm, TextForm, PersonLocationRelationForm
from .forms import location_formset, helper
from django.forms import inlineformset_factory


class LocationView(generic.ListView):
	template_name = 'catalogue/location_list.html'
	context_object_name = 'location_list'

	def get_queryset(self):
		return Location.objects.order_by('name')

class PersonView(generic.ListView):
	template_name = 'catalogue/person_list.html'
	context_object_name = 'person_list'

	def get_queryset(self):
		return Person.objects.order_by('last_name')

class TextView(generic.ListView):
	template_name = 'catalogue/text_list.html'
	context_object_name = 'text_list'

	def get_queryset(self):
		return Text.objects.order_by('title')


def person_detail(request, person_id):
	p = Person.objects.get(pk=person_id)
	form = PersonForm(instance=p)
	print(form.instance.view())
	return render(request,'catalogue/add_person.html',{'form':form})

def add_text(request):
	# if this is a post request we need to process the form data
	if request.method == 'POST':
		form = PersonForm(request.POST)
		if form.is_valid():
			print(f'form is valid: {form.cleaned_data}',type(form))
			form.save()
			return HttpResponseRedirect('/text/')
	else:
		form = TextForm()
	var = {'form':form,'page_name':'Add text'}
	return render(request, 'catalogue/add_text.html', var)


def _handle_date(goal_object,form,names=None):
	if names == None: 
		names = 'date,start_date,end_date,start_spec,end_spec'
	date_name,start_date,end_date,start_spec,end_spec = names.split(',')
	f = form
	print(f,goal_object.pk)
	print(names)
	try: date = getattr(goal_object,date_name)
	except: date = None
	print(date)
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
	# formset.save(commit=False)
	plrs = formset.save(commit = False)
	print(9,plrs[0])
	for f,plr in zip(formset.cleaned_data,plrs):
		print(f,f['DELETE'],111222)
		if f['DELETE']:continue
		if not f['location']: continue
		'''
		d = Date(start=f['start_date'],end=f['end_date'],
			start_specificity=f['start_spec'],
			end_specificity=f['end_spec'])
		d.save()
		print(d.view())
		# print(plr.date.view(),'---')
		plr.date = d
		# print(plr.date.view(),'-0-')
		plr.save()
		'''
		print(plr,8)
		_handle_date(plr,f)
	print('--')
	[obj.delete() for obj in formset.deleted_objects]

def _handle_person_form(form):
	f = form.cleaned_data
	'''
	print(f,f['date_of_death'],type(f['date_of_death']))
	d = Date(start=f['date_of_birth'],end=f['date_of_death'],
		start_specificity=f['birth_spec'],end_specificity=f['death_spec'])
	print(d.view())
	d.save()
	person= form.save()
	print(person.view())
	# print(person.birth_death_date.view(),9)
	person.birth_death_date = d
	# print(person.birth_death_date.view(),0)
	person.save()
	'''
	person= form.save()
	names = 'birth_death_date,date_of_birth,date_of_death,birth_spec,death_spec'
	_handle_date(person,f,names=names)
	return person
	


def add_person(request):
	# if this is a post request we need to process the form data
	if request.method == 'POST':
		form = PersonForm(request.POST)
		if form.is_valid():
			person = _handle_person_form(form)
			formset = location_formset(request.POST, request.FILES, instance=person)
			if formset.is_valid():
				_handle_plr_formset(formset)
				'''
				plrs = formset.save(commit = False)
				for f,plr in zip(formset.cleaned_data,plrs):
					print(f)
					d = Date(start=f['start_date'],end=f['end_date'],
						start_specificity=f['start_spec'],
						end_specificity=f['end_spec'])
					d.save()
					print(d.view())
					plr.date = d
					plr.save()
				print('--')
				# plr.date = d
				'''
				return HttpResponseRedirect(reverse('catalogue:edit_person', 
					args=[person.pk]))
	form = PersonForm()
	formset = location_formset()
	page_name = 'Add Person'
	var = {'form':form,'formset':formset,'page_name':page_name}
	return render(request, 'catalogue/add_person.html', var)


def edit_person(request, person_id):
	person = Person.objects.get(pk=person_id)
	if request.method == 'POST':
		formset = location_formset(request.POST, request.FILES, instance=person)
		form = PersonForm(request.POST,instance=person)
		if form.is_valid() and formset.is_valid():
			person = _handle_person_form(form)
			_handle_plr_formset(formset)
			return HttpResponseRedirect(reverse('catalogue:edit_person', 
				args = [person.pk]))
	form = PersonForm(instance=person)
	sd, ed = form.fields['date_of_birth'], form.fields['date_of_death']
	ss, es = form.fields['birth_spec'], form.fields['death_spec']
	bdd = form.instance.birth_death_date
	print(bdd)
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
		
			print(sd.initial, ed.initial,ss.initial,es.initial)
	# print(form.instance.birth_death_date)
	# print(form.instance,formset.instance)
	page_name = 'Edit Person'
	var = {'form':form,'formset':formset,'page_name':page_name}
	return render(request, 'catalogue/add_person.html',var)


def add_person_location_relation(request, person_id=None):
	# if this is a post request we need to process the form data
	if request.method == 'POST':
		form = PersonForm(request.POST)
		if form.is_valid():
			print(f'form is valid: {form.cleaned_data}',type(form))
			# form.instance.residence = form.cleaned_data["residence"]#[0]
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
			print(f'form is valid: {form.cleaned_data}')
			form.save()
			return HttpResponseRedirect('/admin/catalogue/location/')
	else:
		form = LocationForm()
	var = {'form':form,'page_name':'Add location'}
	return render(request, 'catalogue/add_location.html', var)



# Create your views here.
