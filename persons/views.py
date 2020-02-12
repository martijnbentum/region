from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
from utilities.models import Date 
from .models import Person, PersonLocationRelation
from .forms import PersonForm, PersonLocationRelationForm
from .forms import location_formset 
from django.forms import inlineformset_factory
import json
from locations.models import UserLoc


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
			formset = location_formset(request.POST, instance=person)
			if formset.is_valid():
				formset.save()
			return HttpResponseRedirect(reverse('persons:edit_person', 
				args=[person.pk]))
	form = PersonForm()
	formset = location_formset()
	page_name = 'Add Person'
	var = {'form':form,'formset':formset,'page_name':page_name}
	return render(request, 'persons/add_person.html', var)


def edit_person(request, person_id):
	'''edit person instance and person location relation
	'''
	form, formset= None, None
	person = Person.objects.get(pk=person_id)
	if request.method == 'POST':
		form = PersonForm(request.POST,instance=person)
		if form.is_valid(): 
			print('form is valid: ',form.cleaned_data,type(form))
			person = form.save()
			formset = location_formset(request.POST,instance=person)
			if formset.is_valid() == True:
				print('formset is valid: ',formset.cleaned_data,type(formset))
				formset.save()
				return HttpResponseRedirect(reverse('persons:edit_person', 
					args = [person.pk]))
			else:  
				print('formset invalid', formset.errors)
		else:  print('form invalid', form.errors)
	if formset ==None:formset = location_formset(instance=person)
	if form == None: form = PersonForm(instance=person)
	page_name = 'Edit Person'
	var = {'form':form,'formset':formset,'page_name':page_name}
	return render(request, 'persons/add_person.html',var)


# Create your views here.
