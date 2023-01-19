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
from .forms import LocationRelationForm, LocationTypeForm,LocationStatusForm
from .forms import LocationPrecisionForm
import json
import os
from utils.view_util import make_tabs,FormsetFactoryManager
from utils.map_util import gps2latlng, pop_up, get_all_location_ids_dict
from utils.model_util import instance2names
from utils import text_connection
from utils.search_view_helper import SearchView
from utils.instance_links import Links
from utilities.views import getfocus, list_view, delete_model, edit_model
from utilities.views import add_simple_model
from utilities import search
from catalogue.models import Text, Illustration, Publication, Publisher, Periodical
from persons.models import Person, Movement
import time


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
    c = 'def add_'+make_fname(name)+'(request,pk =None):\n'
    c += '\treturn add_simple_model(request,__name__,"'+name
    c +='","locations","add '+name+'",pk=pk)'
    return exec(c,globals())

#create simple forms for the following models 
names = 'LocationType,LocationPrecision,LocationStatus'
for name in names.split(','):
    create_simple_view(name)



def map_ll(request):
    '''current map view with new map implementation; 
    this new map view uses ajax/ lazy loading to speed up map rendering
    '''
    maplist = [x.plot() for x in get_querysets()]
    args = {'page_name':'map','maplist':maplist}
    return render(request,'locations/map_ll.html',args)


def map_ll_alpha(request):
    '''current map view with new map implementation; 
    this new map view uses ajax/ lazy loading to speed up map rendering
    '''
    d = get_all_location_ids_dict(add_names_gps = True)
    args = {'page_name':'map','d':d}
    return render(request,'locations/map_ll_alpha.html',args)

def map_search(request):
    s = SearchView(request)
    instances = s.search.filter()
    d = get_all_location_ids_dict(instances = instances, add_names_gps = True)
    s.var['page_name']='map search'
    s.var['d']=d
    return render(request, 'locations/map_search.html',s.var)



def map(request):
    '''old style map rendering, all data is prepared beforehand which 
    resulted in slow loading times
    '''
    # maplist = queryset2maplist(get_querysets())
    maplist = None
    args = {'page_name':'map','maplist':maplist}
    return render(request,'locations/map.html',args)

    
def show_links(request,app_name,model_name,pk):
    '''OBSOLETE old style map rendering, render location by getting extra info
    for specific instation to plot the links an instance has to other instances
    which are also plotted on the map
    '''
    print(app_name,model_name,pk)
    instance = apps.get_model(app_name,model_name).objects.get(pk=pk)
    l = Links(instance)
    print(l.connections.instances,22222222222)
    link_list= instance2maprows(instance,role='main') 
    l, fn,ll= instance2related_locations(instance)
    link_list.extend(ll)
    print(link_list,1111111111111111111111111)
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

def ajax_popup(request,markerid,main_instance_markerid = None):
    '''create a popup based on an async call with the relevant information
    '''
    print(markerid,main_instance_markerid,11111111111)
    app_name, model_name, pk,gps= markerid.split('_')
    latlng = gps2latlng(gps)
    model = apps.get_model(app_name,model_name)
    instance = model.objects.get(pk=pk)
    if main_instance_markerid:
        mi_an, mi_mn, mi_pk,mi_gps= main_instance_markerid.split('_')
        mi_model = apps.get_model(mi_an,mi_mn)
        mi_instance = mi_model.objects.get(pk=mi_pk)
        d = {'popup':instance.pop_up(mi_instance)}
    else:d = {'popup':instance.pop_up(latlng)}
    return JsonResponse(d)

def ajax_links(request,markerid):
    '''show links an instance has with other instance by plotting all on a map.
    '''
    app_name, model_name, pk,gps= markerid.split('_')
    model = apps.get_model(app_name,model_name)
    instance = model.objects.get(pk=pk)
    return JsonResponse({'links':Links(instance).plots})

def ajax_instance(request,app_name,model_name,pk):
    '''returns an instance base on app_name model_name and pk.'''
    model = apps.get_model(app_name,model_name)
    print(model,'model')
    instance = model.objects.get(pk=pk)
    print(instance,'instance')
    f = serializers.serialize('json',[instance])
    print(f,'serial')
    return JsonResponse({'instance':f})

def ajax_instances(request,app_name,model_name,pks):
    '''returns an instance base on app_name model_name and pk.'''
    start = time.time()
    model = apps.get_model(app_name,model_name)
    print('model',time.time() - start)
    print(model,'model')
    pks = pks.split(',')
    instances = model.objects.filter(pk__in = pks)
    print('instances',time.time() - start)
    print(instances,'instances')
    d = [x.sidebar_info for x in instances]
    print('info',time.time() - start)
    #d = serializers.serialize('json',instances)
    # print(d,'serial')
    return JsonResponse({'instances':d})
    
def ajax_get_connections(request, app_name, model_name, pk):
    model = apps.get_model(app_name,model_name)
    print(model,'model')
    instance = model.objects.get(pk=pk)
    print(instance,'instance')
    f = serializers.serialize('json',[instance])
    print(f,'serial')
    connections = text_connection.text_connection(instance)
    d=get_all_location_ids_dict(instances=connections.all_texts,add_names_gps=True)
    return JsonResponse({'instances':d,'connection_dict':connections.to_dict()})
    

def geojson_file(request,filename):
    '''files used to draw a figure on a map.
    code for source of life map demo
    '''
    if not os.path.isfile('media/geojson/'+filename): data = {'file':False}
    a =  open('media/geojson/'+filename).read()
    try: data = json.loads(a)
    except: data = {'json':False}
    return JsonResponse(data)


def map_draw(request):
    '''view map demo source of life.
    '''
    f = Figure.objects.all()
    f = serializers.serialize('json',f)
    f = json.loads(f)
    s = Style.objects.all()
    s = serializers.serialize('json',s)
    s = json.loads(s)
    args = {'page_name':'map_draw','figures':f,'styles':s}
    return render(request,'locations/map_draw.html',args)

def edit_style(request, pk=None, focus = '', view='complete'):
    '''source of life map demo.
    '''
    return edit_model(request, __name__,'Style','locations',pk, 
        focus = focus, view=view)

def edit_figure(request, pk=None, focus = '', view='complete'):
    '''source of life map demo.
    '''
    return edit_model(request, __name__,'Figure','locations',pk, 
        focus = focus, view=view)

def style_list(request):
    '''source of life map demo
    '''
    return list_view(request, 'Style', 'locations')

def figure_list(request):
    '''source of life map demo
    '''
    return list_view(request, 'Figure', 'locations')
# Create your views here.

