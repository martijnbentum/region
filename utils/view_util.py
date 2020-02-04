from django.apps import apps
import inspect
import sys

def get_modelform(namespace,modelform_name):
	temp = sys.modules[namespace]
	classes = dict(inspect.getmembers(temp,inspect.isclass))
	try: return classes[modelform_name]
	except: 
		raise ValueError(
			'could not find',modelform_name,'in',classes,'did you import it?')


def _wip_edit_model(request, instance_id, app_name, model_name):
	#WORK IN PROGRESS: should get modelform or import all model forms
	'''edit view generalized over models.
	assumes a 'add_{{model_name}}.html template and edit_{{model_name}} function
	and {{model_name}}Form
	'''
	model = apps.get_model(app_name,model_name)
	modelform = get_modelform(__name__,model_name+'Form')
	instance= model.objects.get(pk=instance_id)
	if request.method == 'POST':
		form = modelform(request.POST, instance=instance)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(
				reverse(app_name+':edit_'+model_name.lower(), 
				args = [instance.pk]))
	form = modelform(instance=instance)
	args = {'form':form,'page_name':'Edit '+model_name.lower()}
	return render(request,app_name+'/add_' + model_name.lower() + '.html',args)
		
