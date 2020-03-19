from django.apps import apps
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from utils import view_util
		

def add_simple_model(request, name_space,model_name,app_name, page_name):
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
	if 'focus' in request.POST.keys():
		return request.POST['focus']
	else: return ''
# Create your views here.

def close(request):
	return render(request,'utilities/close.html')
