from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from utils import view_util
from utils.view_util import Crud, Cruds, make_tabs, FormsetFactoryManager


@login_required
def edit_model(request, name_space, model_name, app_name, instance_id = None, 
	formset_names='', focus='', view ='complete'):
	'''edit view generalized over models.
	assumes a 'add_{{model_name}}.html template and edit_{{model_name}} function
	and {{model_name}}Form
	'''
	names = formset_names
	model = apps.get_model(app_name,model_name)
	modelform = view_util.get_modelform(name_space,model_name+'Form')
	instance= model.objects.get(pk=instance_id) if instance_id else None
	crud = Crud(instance) if instance else None
	ffm, form = None, None
	if request.method == 'POST':
		focus = getfocus(request)
		form = modelform(request.POST, request.FILES, instance=instance)
		if form.is_valid():
			print('form is valid: ',form.cleaned_data,type(form))
			instance = form.save()
			if view == 'complete':
				ffm = FormsetFactoryManager(name_space,names,request,instance)
				valid = ffm.save()
				if valid:
					messages.success(request, model_name + ' saved')
					return HttpResponseRedirect(reverse(
						app_name+':edit_'+model_name.lower(), 
						kwargs={'pk':instance.pk,'focus':focus}))
				else: print('ERROR',ffm.errors)
			else: return HttpResponseRedirect('/utilities/close/')
	if not form: form = modelform(instance=instance)
	if not ffm: ffm = FormsetFactoryManager(name_space,names,instance=instance)
	tabs = make_tabs(model_name.lower(), focus_names = focus)
	page_name = 'Edit ' +model_name.lower() if instance_id else 'Add ' +model_name.lower()
	args = {'form':form,'page_name':page_name,'crud':crud,
		'tabs':tabs, 'view':view}
	args.update(ffm.dict)
	return render(request,app_name+'/add_' + model_name.lower() + '.html',args)
		

def add_simple_model(request, name_space,model_name,app_name, page_name):
	'''Function to add simple models with only a form could be extended.
	request 	django object
	name_space 	the name space of the module calling this function (to load forms / models)
	model_name 	name of the model
	app_name 	name of the app
	page_name 	name of the page
	The form name should be of format <model_name>Form
	'''
	modelform = view_util.get_modelform(name_space,model_name+'Form')
	form = modelform(request.POST)
	if request.method == 'POST':
		if form.is_valid():
			form.save()
			messages.success(request, model_name + ' saved')
			return HttpResponseRedirect('/utilities/close/')
	model = apps.get_model(app_name,model_name)
	instances = model.objects.all().order_by('name')
	var = {'form':form, 'page_name':page_name, 'instances':instances}
	return render(request, 'utilities/add_simple_model.html',var)


def getfocus(request):
	'''extracts focus variable from the request object to correctly set the active tabs.'''
	if 'focus' in request.POST.keys():
		return request.POST['focus']
	else: return 'default'
# Create your views here.

def close(request):
	'''page that closes itself for on the fly creation of model instances (loaded in a new tab).'''
	return render(request,'utilities/close.html')
