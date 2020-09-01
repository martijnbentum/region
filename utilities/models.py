from django.apps import apps
from django.db import models
from django.utils import timezone
from utils.model_util import id_generator, info


class SimpleModel(models.Model):
    name = models.CharField(max_length=300,default='',unique=True)

    def __str__(self): 
        return self.name
                     
    class Meta:        
        abstract=True 

class generic(models.Model):
	pass


class Language(models.Model, info):
	name = models.CharField(max_length=100, unique = True)
	iso = models.CharField(max_length=3,null=True,blank=True)

	def __str__(self):
		return self.name
# Create your models here.

def copy_complete(instance, commit = True):
	'''copy a model instance completely with all relations.'''
	copy = simple_copy(instance, commit)
	app_name, model_name = instance2names(instance)
	for f in copy._meta.get_fields():
		if f.one_to_many:
			for r in list(getattr(instance,f.name+'_set').all()):
				rcopy = simple_copy(r,False)
				setattr(rcopy,model_name.lower(), copy)
				rcopy.save()
		if f.many_to_many:
			getattr(copy,f.name).set(getattr(instance,f.name).all())
	return copy


def simple_copy(instance, commit = True):
	'''Copy a model instance and save it to the database.
	m2m and relations are not saved.
	'''
	app_name, model_name = instance2names(instance)
	model = apps.get_model(app_name,model_name)
	copy = model.objects.get(pk=instance.pk)
	copy.pk = None
	if commit:
		copy.save()
	return copy

def instance2names(instance):
	s = str(type(instance)).split("'")[-2]
	app_name,_,model_name = s.split('.')
	return app_name, model_name

def instance2name(instance):
	app_name, model_name = instance2names(instance)
	return model_name

