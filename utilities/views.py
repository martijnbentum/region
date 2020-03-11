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
			return HttpResponseRedirect('/catalogue/close/')
	model = apps.get_model(app_name,model_name)
	instances = model.objects.all().order_by('name')
	var = {'form':form, 'page_name':page_name, 'instances':instances}
	return render(request, 'persons/add_simple_model.html',var)


def getnavs(request):
	'''navs are variables to set the active tabs on a page.
	navbar is the tab link
	navcontent is the content link
	'''
	navbar, navcontent = 'default', None
	if 'navbar' in request.POST.keys():
		navbar = request.POST['navbar']
	if 'navcontent' in request.POST.keys():
		navcontent= request.POST['navcontent']
	return navbar,navcontent


def listify_navs(navbar,navcontent):
	'''nav variables are csv in the url, need to transform them in a list.'''
	if ',' in navbar: navbar = navbar.split(',')
	if navcontent !=None: navcontent = navcontent.split(',')
	return navbar,navcontent


def getfocus(request):
	if 'focus' in request.POST.keys():
		return request.POST['focus']
	else: return ''
# Create your views here.
