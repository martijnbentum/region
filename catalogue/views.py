from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from .models import Person
from .forms import PersonForm, LocationForm

class PersonView(generic.ListView):
	template_name = 'catalogue/index.html'
	context_object_name = 'person_list'

	def get_queryset(self):
		return Person.objects.order_by('last_name')

def add_person(request):
	# if this is a post request we need to process the form data
	if request.method == 'POST':
		form = PersonForm(request.POST)
		if form.is_valid():
			print(f'form is valid: {form.cleaned_data}',type(form))
			form.instance.residence = form.cleaned_data["residence"][0]
			form.save()
			return HttpResponseRedirect('/person/')
	else:
		form = PersonForm()
	var = {'form':form,'page_name':'Add person'}
	return render(request, 'catalogue/add_person.html', var)
	

def get_locationname(request):
	# if this is a post request we need to process the form data
	if request.method == 'POST':
		form = LocationForm(request.POST)
		if form.is_valid():
			print(f'form is valid: {form.cleaned_data}')
			form.save()
			return HttpResponseRedirect('/admin/catalogue/location/')
	else:
		form = LocationForm()
	var = {'form':form,'page_name':'location'}
	return render(request, 'catalogue/location.html', var)



# Create your views here.
