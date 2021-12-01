from django.apps import apps
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.forms import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from utils.view_util import Crud, Cruds, make_tabs, FormsetFactoryManager
from utils.model_util import copy_complete, identifiers2instances 
from utilities.search import Search
from .models import Comment
from .forms import CommentForm, TimelineForm
import json
from utils import view_util, help_util, make_timeline
from utils import get_totals as gt
from utils import location_to_linked_instances as ltli
import time

def overview(request):
	totals = gt.get_totals()
	total = sum(totals.values())
	countries = gt.get_countries()
	perc_gender = gt.get_perc_gender()
	perc_text_genres = gt.get_perc_text_genres()
	perc_text_types= gt.get_perc_text_types()
	perc_publication_types= gt.get_perc_publication_types()
	perc_illustration_categories= gt.get_perc_illustration_categories()
	perc_illustration_types= gt.get_perc_illustration_types()
	perc_movement_types= gt.get_perc_movement_types()
	var = {'page_name':'overview','totals':totals, 'total':total}
	var.update({'countries':countries,'perc_gender':perc_gender})
	var.update({'perc_text_genres':perc_text_genres})
	var.update({'perc_text_types':perc_text_types})
	var.update({'perc_publication_types':perc_publication_types})
	var.update({'perc_illustration_categories':perc_illustration_categories})
	var.update({'perc_illustration_types':perc_illustration_types})
	var.update({'perc_movement_types':perc_movement_types})
	return render(request,'utilities/overview.html',var)

def timeline(request):
	# model_name = get_timeline_info(request)
	model = None
	form = None
	tjson = ''
	if request.method == 'POST':
		form = TimelineForm(request.POST, request.FILES)
		t= make_timeline.Timelines(form)
		print('timelines:',t.timelines,t.names,t.ncategories)
		tjson = t.make_json()
	if not form: form = TimelineForm()
	var = {'page_name':'timeline','form':form,'tjson':tjson}
	return render(request,'utilities/timeline_test.html',var)

def ajax_identifiers_to_instances(request,identifiers):
	'''returns an instance based on identifier: app_name model_name and pk.
	e.g. catalogue_text_644
	'''
	if type(identifiers) == str:identifiers = identifiers.split(',')
	instances = identifiers2instances(identifiers)
	print(instances,'instances')
	d = [x.sidebar_info for x in instances]
	#d = serializers.serialize('json',instances)
	print(d,'serial')
	return JsonResponse({'instances':d})

def list_view(request, model_name, app_name, max_entries=500):
	'''list view of a model.'''
	extended_search = getextended_search(request)
	active_fields= get_active_search_buttons(request)
	special_terms= get_active_special_term_buttons(request)
	print(special_terms,999)
	s = Search(request,model_name,app_name,active_fields=active_fields,
		special_terms = special_terms, max_entries = max_entries)
	instances= s.filter()
	print('done filtering')
	print('empty query:',s.query.empty)
	var = {model_name.lower() +'_list':instances,
		'page_name':model_name,
		'order':s.order.order_by,'direction':s.order.direction,
		'app_name':app_name,
		'query':s.query.query,'nentries':s.nentries,
		'search_fields':s.search_fields,
		'name':model_name.lower(),'extended_search':extended_search,
		'active_search_buttons':active_fields,
		'active_special_term_buttons':special_terms}
	print(s.notes,000,'<----')
	return render(request, app_name+'/'+model_name.lower()+'_list.html',var)


@permission_required('utilities.add_generic')
def edit_model(request, name_space, model_name, app_name, instance_id = None, 
	formset_names='', focus='default', view ='complete'):
	'''edit view generalized over models.
	assumes a 'add_{{model_name}}.html template and edit_{{model_name}} function
	and {{model_name}}Form
	'''
	start = time.time()
	names = formset_names
	model = apps.get_model(app_name,model_name)
	modelform = view_util.get_modelform(name_space,model_name+'Form')
	print('get model and form',delta(start))
	instance= model.objects.get(pk=instance_id) if instance_id else None
	crud = Crud(instance) if instance and model_name != 'Location' else None
	print('get crud',delta(start))
	ffm, form = None, None
	if request.method == 'POST':
		focus, button = getfocus(request), getbutton(request)
		if button in 'delete,cancel,confirm_delete': 
			return delete_model(request,name_space,model_name,app_name,instance_id)
		copy_instance = copy_complete(instance) if button == 'saveas' and instance else False
		form = modelform(request.POST, request.FILES, instance=instance)
		print('made form in post',delta(start))
		
		if form.is_valid() or copy_instance:
			print('form is valid: ',form.cleaned_data,type(form))
			if not button == 'saveas':instance = form.save()
			else:instance = copy_instance
			if view == 'complete':
				ffm = FormsetFactoryManager(name_space,names,request,instance)
				valid = ffm.save()
				print('formset factory manager / form making done',delta(start))
				if valid:
					print('validated form',delta(start))
					show_messages(request,button, model_name)
					if button== 'add_another':
						return HttpResponseRedirect(reverse(app_name+':add_'+model_name.lower()))
					return HttpResponseRedirect(reverse(
						app_name+':edit_'+model_name.lower(), 
						kwargs={'pk':instance.pk,'focus':focus}))
				else: print('ERROR',ffm.errors)
			else: return HttpResponseRedirect('/utilities/close/')
		else:
			print('form invalid:',form.non_field_errors()[0])
			show_messages(request,'form_invalid', model_name, form)

	print('post part done',delta(start))
	if not form: form = modelform(instance=instance)
	if not ffm: ffm = FormsetFactoryManager(name_space,names,instance=instance)
	print('(after post formset factory manager / form making done',delta(start))
	tabs = make_tabs(model_name.lower(), focus_names = focus)
	print('tabs made',delta(start))
	page_name = 'Edit ' +model_name.lower() if instance_id else 'Add ' +model_name.lower()
	helper = help_util.Helper(model_name=model_name)
	print('helper made',delta(start))
	args = {'form':form,'page_name':page_name,'crud':crud,'model_name':model_name,
		'app_name':app_name,'tabs':tabs, 'view':view,'helper':helper.get_dict(),
		'instance':instance}
	args.update(ffm.dict)
	print('arg made, start rendering',delta(start))
	return render(request,app_name+'/add_' + model_name.lower() + '.html',args)
		

@permission_required('utilities.add_generic')
def add_simple_model(request, name_space,model_name,app_name, page_name, pk = None):
	'''Function to add simple models with only a form could be extended.
	request 	django object
	name_space 	the name space of the module calling this function (to load forms / models)
	model_name 	name of the model
	app_name 	name of the app
	page_name 	name of the page
	The form name should be of format <model_name>Form
	'''
	model = apps.get_model(app_name,model_name)
	modelform = view_util.get_modelform(name_space,model_name+'Form')
	instance= model.objects.get(pk=pk) if pk else None
	# form = modelform(request.POST)
	form = None
	if request.method == 'POST':
		form = modelform(request.POST, instance=instance)
		button = getbutton(request) 
		if button in 'delete,confirm_delete':
			print('deleting simple model')
			return delete_model(request,name_space,model_name,app_name,pk,True)
		if form.is_valid():
			form.save()
			messages.success(request, model_name + ' saved')
			return HttpResponseRedirect('/utilities/close/')
	if not form: form = modelform(instance=instance)
	instances = model.objects.all().order_by('name')
	page_name = 'Edit ' +model_name.lower() if pk else 'Add ' +model_name.lower()
	url = '/'.join(request.path.split('/')[:-1])+'/' if pk else request.path
	var = {'form':form, 'page_name':page_name, 'instances':instances, 'url':url}
	return render(request, 'utilities/add_simple_model.html',var)

@permission_required('utilities.delete_generic')
def delete_model(request, name_space, model_name, app_name, pk, close = False):
	model = apps.get_model(app_name,model_name)
	instance= get_object_or_404(model,id =pk)
	focus, button = getfocus(request), getbutton(request)
	if request.method == 'POST':
		if button == 'cancel': 
			show_messages(request,button, model_name)
			return HttpResponseRedirect(reverse(
				app_name+':edit_'+model_name.lower(), 
				kwargs={'pk':instance.pk,'focus':focus}))
		if button == 'confirm_delete':
			instance.delete()
			show_messages(request,button, model_name)
			if close: return HttpResponseRedirect('/utilities/close/')
			return HttpResponseRedirect('/utilities/list_view/'+model_name.lower()+'/' +app_name)
	info = instance.info
	var = {'info':info,'page_name':'Delete '+model_name.lower()}
	return render(request, 'utilities/delete_model.html',var)
	

def getfocus(request):
	'''extracts focus variable from the request object to correctly set the active tabs.'''
	if 'focus' in request.POST.keys():
		focus = request.POST['focus']
		if focus == '': return 'default'
		else: return focus
	else: return 'default'
# Create your views here.
def getbutton(request):
	if 'save' in request.POST.keys():
		return request.POST['save']
	else: return 'default'

def getextended_search(request):
	print(request.GET)
	if 'extended_search' in request.GET.keys():
		return request.GET['extended_search']
	else: return 'display:block'

def get_active_search_buttons(request):
	print(request.GET)
	if 'active_search_buttons' in request.GET.keys():
		return request.GET['active_search_buttons'].split(',')
	else: return []

def get_active_special_term_buttons(request):
	print(request.GET)
	if 'active_special_term_buttons' in request.GET.keys():
		return request.GET['active_special_term_buttons'].split(',')
	else: return []



def show_messages(request,message_type,model_name,form=None):
	'''provide user feedback on submitting a form.'''
	print(message_type)
	if message_type == 'saveas':messages.warning(request,
		'saved a copy of '+model_name+'. Use "save" button to store edits to this copy')
	elif message_type == 'confirm_delete':messages.success(request, model_name + ' deleted')
	elif message_type == 'cancel':messages.warning(request,'delete aborted')
	elif message_type == 'form_invalid':
		for error in form.non_field_errors():
			messages.warning(request,error)
	else: messages.success(request, model_name + ' saved')

def close(request):
	'''page that closes itself for on the fly creation of model instances (loaded in a new tab).'''
	return render(request,'utilities/close.html')

def edit_comment(request, app_name='', model_name='',entry_pk=None,user_pk=None):
	if app_name and model_name:
		model = apps.get_model(app_name,model_name)
		instance = model.objects.get(pk=entry_pk)
		crud = Crud(instance)
		print('commentator',request.user)
		print('addressee',crud.contributers)
		app_name, model_name = app_name.lower(), model_name.lower()
	extra = 0 if user_pk else 1
	CommentFormset = modelformset_factory(Comment, CommentForm,
		fields=('subject','comment','fixed'), extra=extra, can_delete=True)
	if user_pk: 
		user = get_user_model().objects.get(pk = user_pk)
		queryset = Comment.objects.filter(user_addressee__icontains = user.username)
	else:
		queryset=Comment.objects.filter(app_name=app_name,model_name=model_name,entry_pk=entry_pk)
	formset =[]
	if request.method == 'POST':
		formset = CommentFormset(request.POST,queryset=queryset)
		if formset.is_valid():
			instances = formset.save(commit=False)
			for x in instances:
				if user_pk: x.save()
				else:_handle_comment(x,app_name,model_name,entry_pk,crud.contributers,request.user)
			for obj in formset.deleted_objects:
				obj.delete()
			print('save is a success')
			if not user_pk: return render(request,'utilities/close.html')
		else: print('not valid',formset.errors,app_name,model_name,entry_pk)
	if not formset: formset = CommentFormset(queryset=queryset)
	if user_pk: 
		page_name = 'Comments addressed to: ' 
		user_comment = True
	else: 
		page_name = 'Comments about: ' + str(instance)
		user_comment = False
	var = {'formset':formset,'page_name':page_name,'model_name':model_name,
		'user_comment':user_comment}
	return render(request, 'utilities/add_comment.html',var)

def _handle_comment(instance,app_name,model_name,entry_pk,user_addressee,user_commentator):
	print('saving comment:',instance,entry_pk,user_addressee,user_commentator)
	if not instance.app_name: instance.app_name = app_name
	if not instance.model_name: instance.model_name = model_name
	if not instance.entry_pk: instance.entry_pk=entry_pk 
	if not instance.user_addressee: instance.user_addressee=user_addressee
	if not instance.user_commentator: instance.user_commentator=user_commentator
	instance.save()
	

def delta(start):
	return time.time() - start
