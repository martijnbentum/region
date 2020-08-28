from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
from django.forms import inlineformset_factory
from .models import Location, LocationType, LocationRelation
from .forms import LocationForm, location_relation_formset
from .forms import LocationRelationForm, LocationTypeForm,LocationStatusForm,LocationPrecisionForm
import json
from utils.view_util import make_tabs,FormsetFactoryManager
from utilities.views import getfocus, list_view, delete_model, edit_model, add_simple_model


def make_fname(name):
	o = name[0]
	for c in name[1:]:
		if c.isupper(): o+= '_' + c
		else: o += c
	return o.lower()

def create_simple_view(name):
    '''Create a simple view based on the Model name.
    Assumes the form only has a name field.
    '''
    c = 'def add_'+make_fname(name)+'(request):\n'
    c += '\treturn add_simple_model(request,__name__,"'+name+'","locations","add '+name+'")'
    return exec(c,globals())

#create simple forms for the following models 
names = 'LocationType,LocationPrecision,LocationStatus'
for name in names.split(','):
    create_simple_view(name)


def location_list(request):
	'''list view of location.'''
	return list_view(request, 'Location', 'locations')


class LocationView(generic.ListView):
	template_name = 'locations/location_list.html'
	context_object_name = 'location_list'
	extra_context={'page_name':'Location'}

	def get_queryset(self):
		return UserLoc.objects.order_by('name')[:100]

def edit_location(request, pk=None, focus = '', view='complete'):
	names='location_relation_formset'
	return edit_model(request, __name__,'Location','locations',pk,formset_names=names, 
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





def delete(request, pk, model_name):
	return delete_model(request, __name__,model_name,'locations',pk)
# Create your views here.


# Create your views here.
