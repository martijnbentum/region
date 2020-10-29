from django.apps import apps
from django.core import serializers
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
from django.forms import inlineformset_factory
from .models import Location, LocationType, LocationRelation, Figure,Style 
from .forms import LocationForm, location_relation_formset, StyleForm,FigureForm
from .forms import LocationRelationForm, LocationTypeForm,LocationStatusForm,LocationPrecisionForm
import json
import os
from utils.view_util import make_tabs,FormsetFactoryManager
from utils.map_util import instance2related_locations,queryset2maplist,instance2maprows
from utilities.views import getfocus, list_view, delete_model, edit_model, add_simple_model

from catalogue.models import Text, Illustration, Publication, Publisher, Periodical
from persons.models import Person, Movement




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


def map(request):
	maplist = queryset2maplist(get_querysets())
	args = {'page_name':'map','maplist':maplist}
	return render(request,'locations/map.html',args)

	
def show_links(request,app_name,model_name,pk):
	instance = apps.get_model(app_name,model_name).objects.get(pk=pk)
	link_list= instance2maprows(instance,role='main') 
	l, fn,ll= instance2related_locations(instance)
	link_list.extend(ll)
	args = {'page_name':'links','link_list':link_list}
	return render(request,'locations/map.html',args)



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


def get_querysets(names = None):
	'''load all queryset based on model names in names.
	names can be list or comma seprated string 
	each item should follow this format: app_name$model_name
	'''
	if not names:
		names = 'Text,Illustration,Publication,Publisher,Periodical'.split(',')
		names = ['catalogue$'+name for name in names]
		names.extend('persons$Person,persons$Movement'.split(','))
	if type(names) == str: names = names.spilt(',')
	qs = []
	for name in names:
		app_name,model_name = name.split('$')
		model = apps.get_model(app_name,model_name)
		qs.extend(model.objects.all())
	return qs


def geojson_file(request,filename):
	if not os.path.isfile('media/geojson/'+filename): data = {'file':False}
	a =  open('media/geojson/'+filename).read()
	try: data = json.loads(a)
	except: data = {'json':False}
	return JsonResponse(data)


def map_draw(request):
	f = Figure.objects.all()
	f = serializers.serialize('json',f)
	f = json.loads(f)
	s = Style.objects.all()
	s = serializers.serialize('json',s)
	s = json.loads(s)
	args = {'page_name':'map_draw','figures':f,'styles':s}
	return render(request,'locations/map_draw.html',args)

def edit_style(request, pk=None, focus = '', view='complete'):
	return edit_model(request, __name__,'Style','locations',pk, 
		focus = focus, view=view)

def edit_figure(request, pk=None, focus = '', view='complete'):
	return edit_model(request, __name__,'Figure','locations',pk, 
		focus = focus, view=view)

def style_list(request):
	'''list view of location.'''
	return list_view(request, 'Style', 'locations')

def figure_list(request):
	'''list view of location.'''
	return list_view(request, 'Figure', 'locations')
# Create your views here.

