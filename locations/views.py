from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
from .models import GeoLoc, UserLoc
from .forms import GeoLocForm, FastLocForm ,UserLocForm,geolocrelation_country_formset 
from .forms import geolocrelation_region_formset, region_formset, country_formset
from .forms import geoloc_relation_formset
from django.forms import inlineformset_factory
import json
from utils.view_util import make_tabs,FormsetFactoryManager
from utilities.views import getfocus, list_view, delete_model, edit_model


def location_list(request):
	'''list view of userlocs.'''
	return list_view(request, 'UserLoc', 'locations')

def geoloc_list(request):
	'''list view of geolocs.'''
	return list_view(request, 'GeoLoc', 'locations')

class LocationView(generic.ListView):
	template_name = 'locations/location_list.html'
	context_object_name = 'location_list'
	extra_context={'page_name':'Location'}

	def get_queryset(self):
		return UserLoc.objects.order_by('name')[:100]

def edit_location(request, pk=None, focus = '', view='complete'):
	# names='geoloc_relation_formset'
	# return edit_model(request, __name__,'GeoLoc','locations',pk,formset_names=names, 
	return edit_model(request, __name__,'Location','locations',pk, 
		focus = focus, view=view)



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



def delete(request, pk, model_name):
	return delete_model(request, __name__,model_name,'locations',pk)
# Create your views here.

def userloc2geoloc(ul):
	gls = ul.geoloc_set.all()
	for gl in gls: 
		if gl.name == ul.name: return gl
	return None

# Create your views here.
