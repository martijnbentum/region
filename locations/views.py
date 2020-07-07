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

def edit_geoloc(request, pk=None, focus = '', view='complete'):
	names='geoloc_relation_formset'
	return edit_model(request, __name__,'GeoLoc','locations',pk,formset_names=names, 
		focus = focus, view=view)

def edit_userloc(request, pk=None, focus = '', view='complete'):
	return edit_model(request, __name__,'UserLoc','locations',pk, 
		focus = focus, view=view)

def add_location(request, focus = '', view = 'complete', pk= None):
	request_focus = getfocus(request)
	names = 'geolocrelation_country_formset,geolocrelation_region_formset'
	ffm,l = None,None
	if focus == '': focus = getfocus(request)
	print('focus',focus)
	geoloc=GeoLoc.objects.get(pk=pk) if pk and focus == 'GeoLocation' else None
	userloc=UserLoc.objects.get(pk=pk) if pk and focus == 'UserLocation' else None
	if userloc: 
		geoloc = userloc2geoloc(userloc)
		print(geoloc)
	if request.method == 'POST' and focus != 'Help':
		form = GeoLocForm(request.POST, request.FILES,instance =geoloc)
		fastform = FastLocForm(request.POST)
		userform = UserLocForm(request.POST, instance =userloc)
		# print(userform)
		print(88,form.is_valid())
		if form.is_valid() and ('GeoLocation' in focus or request_focus == 'GeoLocation') :
			print('form is valid: ',form.cleaned_data, 111)
			create_ul = False if geoloc and userloc else True
			l = form.save(create_ul=create_ul)
			print(l)
			if view =='complete':
				ffm = FormsetFactoryManager(__name__,names,request,instance=l)
				print(ffm.dict['geolocrelation_country_formset'].management_form,88)
				valid = ffm.save()
				print(valid,999)
				if valid:
					return HttpResponseRedirect('/locations/')
			else: return HttpResponseRedirect('/utilities/close/')
		elif fastform.is_valid() and focus == 'Add-from-database':
			print('form is valid: ',fastform.cleaned_data)
			fastform.save()
			if view == 'inline': return HttpResponseRedirect('/utilities/close/')
			return HttpResponseRedirect('/locations/')
		elif userform.is_valid() and focus == 'UserLocation':
			print('form is valid: ',userform.cleaned_data)
			userform.save()
			if view == 'inline': return HttpResponseRedirect('/utilities/close/')
			return HttpResponseRedirect('/locations/')
		print(fastform)
	else:
		form = GeoLocForm(instance=geoloc)
		fastform = FastLocForm()
		userform = UserLocForm(instance=userloc)
	if not ffm: ffm = FormsetFactoryManager(__name__,names,instance=geoloc)
	tabs = make_tabs('location',focus_names = focus)
	page_name = 'Edit location' if pk else 'Add location'
	var = {'form':form,'fastform':fastform,'userform':userform,
		'page_name':page_name,'tabs':tabs, 'view':view}
	var.update(ffm.dict)
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



def delete(request, pk, model_name):
	return delete_model(request, __name__,model_name,'locations',pk)
# Create your views here.

def userloc2geoloc(ul):
	gls = ul.geoloc_set.all()
	for gl in gls: 
		if gl.name == ul.name: return gl
	return None

# Create your views here.
