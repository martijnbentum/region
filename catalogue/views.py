from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from .models import Location, Person, Text,PersonLocationRelation
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

class PersonCreate(CreateView):
	model = Person
	template_name = 'catalogue/add_person.html'
	form_class = PersonForm
	success_url = None
	
	def get_context_data(self, **kwargs):
		data = super().get_context_data(**kwargs)
		if self.request.POST:
			data['locations'] = location_formset(self.request.POST)
		else:
			data['locations'] = location_formset()
		return data
	
	def form_valid(self,form):
		context = self.get_context_data()
		locations = context['locations']
		with transaction.atomic():
			form.instance.created_by = self.request.user
			self.object = form.save()
			if locations.is_valid():
				locations.instance = self.object
				locations.save()
		return super(PersonCreate, self).form_valid(form)
		

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


def add_person(request, person_id=None):
	# if this is a post request we need to process the form data
	if person_id: p = Person.objects.get(pk=person_id)
	else:  p = None
	if request.method == 'POST':
		form = PersonForm(request.POST,instance=p)
		formset = location_formset(request.POST,instance=p)
		if form.is_valid():
			print(f'form is valid: {form.cleaned_data}',type(form))
			print(f'formset is valid: {formset.cleaned_data}',type(form))
			# form.instance.residence = form.cleaned_data["residence"]#[0]
			form.save()
			return HttpResponseRedirect('/person/')
	form = PersonForm(instance=p)
	formset = location_formset(instance=p)
	print(form,'\n\n\n',formset)
	if person_id: page_name ='Edit page'
	else: page_name = 'Add Person'
	var = {'form':form,'formset':formset,'helper':helper,'page_name':page_name}
	return render(request, 'catalogue/add_person.html', var)


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
