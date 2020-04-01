from django.apps import apps
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from utils import view_util
		

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
