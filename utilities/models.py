from django.apps import apps
from django.db import models
from django.utils import timezone
from utils.model_util import id_generator, info, instance2names
from utils.map_util import pop_up, get_location_name,gps2latlng

class RelationModel(models.Model):
	'''abstract model for relational models, e.g. text person relation model
		provide other function: gives field name of the other field name
		e.g. in previous example if person is provided text would be returned
	'''
	model_fields = ['','']
	other = False
	other_field_name = False
	relation_field = ''

	class Meta:
		abstract=True

	def set_other(self,main_instance):
		for field_name in self.model_fields:
			instance = getattr(self,field_name)
			if instance == main_instance: continue
			else: 
				self.other = instance
				self.other_field_name =field_name

	def plot(self):
		app_name, model_name = instance2names(self) 
		oan,omn = instance2names(self.other)
		gps = str(self.other.gps.split(' | ')).replace("'",'')
		d = {'app_name':app_name, 'model_name':model_name, 
			'gps':gps, 'pk':self.pk,'layer_name':omn}
		return d

	def pop_up(self,main_instance):
		self.set_other(main_instance)
		if not self.other: return 'could not construct relation'
		latlng = gps2latlng(self.other.gps)
		m = self.other.pop_up(latlng)
		return m


class SimpleModel(models.Model):
	'''abstract model for simple model with only a name and description.'''
	name = models.CharField(max_length=300,default='',unique=True)
	description = models.TextField(blank=True,null=True)
	notes= models.TextField(blank=True,null=True)
	endnode = True

	def __str__(self): 
		return self.name
                     
	class Meta:        
		abstract=True 

class generic(models.Model):
	pass


class Language(models.Model, info):
	name = models.CharField(max_length=100, unique = True)
	iso = models.CharField(max_length=3,null=True,blank=True)
	endnode = True

	def __str__(self):
		return self.name
# Create your models here.

class GroupTag(models.Model,info):
	name = models.CharField(max_length=300)
	created = models.DateTimeField(auto_now_add=True,null=True)
	modified = models.DateTimeField(auto_now_add=False,null=True,blank=True)
	done = models.BooleanField(default=False)
	tag_type = models.CharField(max_length=300,blank=True, null =True)
	index = models.PositiveIntegerField(null=True,blank=True) 
	description = models.TextField(blank=True,null=True)

	def save(self, *args, **kwargs):  
		if not self.id:
			self.created = timezone.now()
		else: self.modified = timezone.now()
		return super(GroupTag, self).save(*args,**kwargs)

	def __lt__(self,other):
		return self.created < other.created

	def __repr__(self):
		return self.name


			






