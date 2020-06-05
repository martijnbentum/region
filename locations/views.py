from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
from .models import GeoLoc, UserLoc
from .forms import GeoLocForm, FastLocForm ,UserLocForm
# from .forms import location_formset, helper
from django.forms import inlineformset_factory
import json
from utils.view_util import make_tabs
from utilities.views import getfocus, list_view, delete_model


def location_list(request):
	'''list view of userlocs.'''
	return list_view(request, 'UserLoc', 'locations')

class LocationView(generic.ListView):
	template_name = 'locations/location_list.html'
	context_object_name = 'location_list'
	extra_context={'page_name':'Location'}

	def get_queryset(self):
		return UserLoc.objects.order_by('name')[:100]


def add_location(request, focus = '', view = 'complete', pk= None):
	if focus == '': focus = getfocus(request)
	print('focus',focus)
	geoloc=GeoLoc.objects.get(pk=pk) if pk and focus == 'GeoLocation' else None
	userloc=UserLoc.objects.get(pk=pk) if pk and focus == 'UserLocation' else None
	if request.method == 'POST' and focus != 'Help':
		form = GeoLocForm(request.POST, instance =geoloc)
		fastform = FastLocForm(request.POST)
		userform = UserLocForm(request.POST, instance =userloc)
		# print(userform)
		if form.is_valid() and focus == 'GeoLocation':
			print('form is valid: ',form.cleaned_data, 111)
			l = form.save()
			if view == 'inline': return HttpResponseRedirect('/utilities/close/')
			return HttpResponseRedirect('/locations/')
		if fastform.is_valid() and focus == 'Add-from-database':
			print('form is valid: ',fastform.cleaned_data)
			fastform.save()
			if view == 'inline': return HttpResponseRedirect('/utilities/close/')
			return HttpResponseRedirect('/locations/')
		if userform.is_valid() and focus == 'UserLocation':
			print('form is valid: ',userform.cleaned_data)
			userform.save()
			if view == 'inline': return HttpResponseRedirect('/utilities/close/')
			return HttpResponseRedirect('/locations/')
		print(fastform)
	else:
		form = GeoLocForm(instance=geoloc)
		fastform = FastLocForm()
		userform = UserLocForm(instance=userloc)
	tabs = make_tabs('location',focus_names = focus)
	page_name = 'Edit location' if pk else 'Add location'
	var = {'form':form,'fastform':fastform,'userform':userform,
		'page_name':page_name,'tabs':tabs, 'view':view}
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

# Create your views here.
