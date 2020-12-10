from django.db import models
from django.conf import settings
from django.utils import timezone
import glob
from locations.models import Location
from utilities.models import Language, RelationModel, SimpleModel, instance2names
from utils.model_util import id_generator, info
from utils.map_util import field2locations, pop_up, get_location_name
import os
from partial_date import PartialDateField
import time

def make_simple_model(name):
	exec('class '+name + '(SimpleModel,info):\n\tpass',globals())

names = 'CopyRight,Genre,TextType,TextTextRelationType,Audience,IllustrationType'
names += ',PublicationType,IllustrationCategory,IllustrationIllustrationRelationType'
names = names.split(',')

for name in names:
	make_simple_model(name)
			

class Item(models.Model):
	'''abstract model for non simple/ non relational catalogue models.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	description = models.TextField(blank=True)
	notes = models.TextField(default='',blank=True, null=True)
	complete = models.BooleanField(default=False)
	approved = models.BooleanField(default=False)
	source_link= models.CharField(max_length=1000,blank=True,null=True)
	copyright = models.ForeignKey(CopyRight,**dargs)
	gps = models.CharField(max_length=300,default ='')
	gps_names = models.CharField(max_length=4000,default='')
	location_field = 'location'
	
	def __str__(self):
		return self.instance_name

	def save(self,*args,**kwargs):
		super(Item,self).save(*args,**kwargs)
		old_gps = self.gps
		self._set_gps()
		if self.gps != old_gps:super(Item,self).save()
		super(Item,self).save(*args,**kwargs)

	def _set_gps(self):
		'''sets the gps coordinates and name of related location to speed up map visualization.'''
		locations = field2locations(self,self.location_field)
		if locations:
			gps = ' | '.join([location.gps for location in locations])
			names= ' | '.join([location.name for location in locations])
			self.gps = gps
			self.gps_names = names
		else: self.gps, self.gps_names = '',''

	@property
	def latlng(self):
		try: return [eval(el) for el in self.gps.split(' - ')]
		except: return None

	@property
	def latlng_names(self):
		try: return self.gps_names.split(' - ')
		except: return None

	@property
	def location_string(self):
		try:return ', '.join(self.latlng_names)
		except: return ''

	def pop_up(self, latlng=None):
		'''creates html for the pop up for map visualization.'''
		return pop_up(self,latlng)	

	@property
	def instance_name(self):
		if hasattr(self,'title'):
			return self.title
		if hasattr(self,'name'):
			return self.name
		if hasattr(self,'caption'):
			return self.caption
		else: raise ValueError('please override instance_name property with correct "name" field')

	@property
	def plot(self):
		app_name, model_name = instance2names(self) 
		gps = str(self.gps.split(' | ')).replace("'",'')
		d = {'app_name':app_name, 'model_name':model_name, 
			'gps':gps, 'pk':self.pk}
		return d

	def gps2name(self,latlng):
		return get_location_name(self,latlng)
	
	class Meta:
		abstract = True



# --- non simple / non relational catalogue models ---

class Text(Item, info):
	'''a text can be an entire book or article or a subsection thereof.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	title = models.CharField(max_length=300)
	setting = models.CharField(max_length=300,blank=True)
	language = models.ForeignKey(Language, **dargs)
	genre = models.ForeignKey(Genre, **dargs)
	text_type = models.ForeignKey(TextType, **dargs)
	# upload = models.FileField(upload_to='texts/',blank=True,null=True) # ?
	relations = models.ManyToManyField('self',
		through='TextTextRelation',symmetrical=False, default=None)
	location= models.ManyToManyField(Location,blank=True, default= None)

	class Meta:
		unique_together = 'title,setting,language'.split(',')

		

def make_filename(instance, filename):
	app_name, model_name = instance2names(instance)
	name,ext = os.path.splitext(filename)
	name += '_django-'+time.strftime('%y-%m-%d-%H-%M') + ext
	pn = model_name.lower() +'/'+ name
	return pn

class Illustration(Item, info):
	'''a illustration typically part of publication'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	caption =  models.CharField(max_length=300,null=True,blank=True)
	category = models.ForeignKey(IllustrationCategory,on_delete=models.SET_NULL,
		blank=True,null=True,related_name='Illustration')
	categories=models.ManyToManyField(IllustrationCategory,blank=True,related_name='Illustrations') 
	page_number = models.CharField(max_length=50, default = '', blank=True)
	upload= models.ImageField(upload_to=make_filename,null=True,blank=True)
	relations = models.ManyToManyField('self',
		through='IllustrationIllustrationRelation',symmetrical=False, default=None)
	illustration_type = models.ForeignKey(IllustrationType, **dargs)
	location_field = ''
	image_filename = models.CharField(max_length=500,default='',blank=True,null=True)

	class Meta:
		unique_together = 'caption,image_filename,page_number'.split(',')

	

class Publisher(Item, info):
	'''Company that publishes works.'''
	name = models.CharField(max_length=300, unique=True)
	location= models.ManyToManyField(Location,blank=True,default=None)
	founded = models.PositiveIntegerField(null=True,blank=True) 
	closure = models.PositiveIntegerField(null=True,blank=True) 


	class Meta:
		ordering = ['name']
		unique_together = 'name,founded'.split(',')


class Publication(Item, info):
	'''The publication of a text or collection of texts and illustrations'''
	title = models.CharField(max_length=300,null=True)
	publisher = models.ManyToManyField(Publisher,blank=True)
	form = models.ForeignKey(PublicationType,on_delete=models.SET_NULL,null=True)
	issue = models.PositiveIntegerField(default=0,blank=True) 
	volume = models.PositiveIntegerField(default=0,blank=True) 
	identifier = models.CharField(max_length=100,null=True,blank=True,unique=True) # not shown 
	year = models.PositiveIntegerField(null=True,blank=True) # obsolete, replace by date
	date = PartialDateField(null=True,blank=True)
	location = models.ManyToManyField(Location,blank=True,default=None) 
	pdf = models.FileField(upload_to='publication/',null=True,blank=True) # ?
	cover = models.ImageField(upload_to='publication/',null=True,blank=True)
	publisher_names = models.CharField(max_length = 500, null=True,blank=True,default='')


	class Meta:
		unique_together = [['title','publisher_names','date','issue','volume']]


	@property
	def publisher_str(self):
		return ' | '.join([x.name for x in self.publisher.all()])
		# return self.publisher_names

	@property
	def location_str(self):
		return ' | '.join([pu.name for pu in self.location.all()])


class Periodical(Item, info):
	'''Recurrent publication.'''
	title = models.CharField(max_length=300)
	founded = models.PositiveIntegerField(null=True,blank=True) 
	closure = models.PositiveIntegerField(null=True,blank=True) 
	location= models.ManyToManyField(Location,blank=True,default =None)


	class Meta:
		unique_together = 'title,founded'.split(',')


# ---- relation objects, e.g text publication relation etc. ----

class TextPublicationRelation(RelationModel): 
	'''Links a text with a publication.'''
	text = models.ForeignKey(Text, on_delete=models.CASCADE)
	publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
	start_page = models.CharField(max_length=5,null=True,blank=True)
	end_page = models.CharField(max_length=5,null=True,blank=True)
	model_fields = ['text','publication']

	def __str__(self):
		try:
			m =  self.text.title+ ' is a part of '
			m += self.publication.title
			return m
		except:
			print('textpublicationrelation name could not be made')
			return ''

	@property
	def primary(self):
		return self.text
		

class TextReviewPublicationRelation(RelationModel): 
	'''Links a text with a publication.'''
	text = models.ForeignKey(Text, on_delete=models.CASCADE)
	publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
	model_fields = ['text','publication']

	def __str__(self):
		m =  self.text.title+ ' is a review of '
		m += self.publication.title
		return m

	@property
	def primary(self):
		return self.text


class IllustrationPublicationRelation(RelationModel): 
	'''Links a illustration with a publication.'''
	illustration = models.ForeignKey(Illustration, on_delete=models.CASCADE)
	publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
	page = models.CharField(max_length=5,null=True,blank=True)
	model_fields = ['illustration','publication']

	def __str__(self):
		m =  self.illustration.caption+ ' is a part of '
		m += self.publication.title
		return m

	@property
	def primary(self):
		return self.illustration


class PeriodicalPublicationRelation(RelationModel, info):
	'''linking a periodical to a publication (a specific issue of a periodical).'''
	periodical= models.ForeignKey(Periodical, on_delete=models.CASCADE)
	publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
	volume= models.PositiveIntegerField(null=True,blank=True)
	issue= models.PositiveIntegerField(null=True,blank=True)
	model_fields = ['periodical','publication']

	def __str__(self):
		m =  self.periodical.title+ ' is a periodical in '
		m += self.publication.title
		return m

	@property
	def primary(self):
		return self.periodical


class TextTextRelation(models.Model, info):
	'''connects two texts with a specific type of relation e.g. original 
	and translation (primary, secondary).'''
	primary = models.ForeignKey('Text', related_name='primary',
									on_delete=models.CASCADE, default=None)
	secondary = models.ForeignKey('Text', related_name='secondary',
									on_delete=models.CASCADE, default=None)
	relation_type = models.ForeignKey(TextTextRelationType, 
									on_delete=models.CASCADE, default=None)
	model_fields = ['primary','secondary']

	def __str__(self):
		m =  self.relation_type.name +' relation between ' + self.secondary.title +' and '
		m += self.primary.title
		return m


class IllustrationIllustrationRelation(models.Model, info):
	'''connects two texts with a specific type of relation e.g. original 
	and translation (primary, secondary).'''
	primary = models.ForeignKey('Illustration', related_name='primary',
									on_delete=models.CASCADE, default=None)
	secondary = models.ForeignKey('Illustration', related_name='secondary',
									on_delete=models.CASCADE, default=None)
	relation_type = models.ForeignKey(IllustrationIllustrationRelationType, 
									on_delete=models.CASCADE, default=None)
	model_fields = ['primary','secondary']

	def __str__(self):
		try:
			m =  self.relation_type.name +' relation between ' + self.secondary.caption+' and '
			m += self.primary.caption
		except:
			print('WARNING, could not create string for IllustrationIllustrationRelation')
			return ''
		return m
