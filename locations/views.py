from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
from .models import GeoLoc 
# from .forms import LocationForm 
# from .forms import location_formset, helper
from django.forms import inlineformset_factory
import json


class LocationView(generic.ListView):
	template_name = 'locations/location_list.html'
	context_object_name = 'location_list'

	def get_queryset(self):
		return GeoLoc.objects.order_by('name')[:100]


def add_location(request):
	# if this is a post request we need to process the form data
	if request.method == 'POST':
		form = LocationForm(request.POST)
		if form.is_valid():
			print('form is valid: ',form.cleaned_data)
			form.save()
			return HttpResponseRedirect('/locations/')
	else:
		form = LocationForm()
	var = {'form':form,'page_name':'Add location'}
	return render(request, 'locations/add_location.html', var)

def mapp(request, location_name = ''):
	if location_name == '': location_name = 'europe'
	map_name = location_name + '.js'
	var = {'map_name':map_name,'location_name':location_name}
	return render(request,'locations/map_location.html',var)

def germany(request):
	location_name = 'germany'
	map_name = location_name + '.js'
	var = {'map_name':map_name,'location_name':location_name}
	return render(request,'locations/markers.html',var)
	

def world(request):
	return render(request,'locations/world.html')

def add_userloc(request, location_name = ''):
	if location_name == '': location_name = 'europe'
	map_name = location_name + '.js'
	ob = request.GET.get('order_by', 'name')
	# if ob == 'country': ob = 'contained_by_country'
	locs = GeoLoc.objects.order_by(ob)[:100]
	var = {'map_name':map_name,'location_name':location_name,
		'location_list':locs}
	return render(request,'locations/add_user_loc.html',var)



# Create your views here.

# Create your views here.
