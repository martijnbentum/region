from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.db.utils import IntegrityError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import json
from locations.models import Location
from utilities.models import Language, RelationModel
from utils.model_util import id_generator, info
from utils.map_util import field2locations, pop_up
from partial_date import PartialDateField
			

class test(models.Model, info):
	name = models.CharField(max_length =9)
	pd = PartialDateField()

class CopyRight(models.Model, info):
	name = models.CharField(max_length=100,unique=True)

	def __str__(self):
		return self.name

class Genre(models.Model, info):
	'''category for texts. '''
	name = models.CharField(max_length=100,unique=True)
	description = models.TextField(blank=True)
	
	def __str__(self):
		return self.name

class TextType(models.Model, info):
	'''category for text model to indicate text text relation . '''
	name = models.CharField(max_length=100,unique=True)
	description = models.TextField(blank=True)
	
	def __str__(self):
		return self.name
	


class Text(models.Model, info):
	'''a text can be an entire book or article or a subsection thereof.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	title = models.CharField(max_length=300)
	text_id= models.CharField(max_length=30,default = '')
	setting = models.CharField(max_length=300,blank=True)
	language = models.ForeignKey(Language, **dargs)
	genre = models.ForeignKey(Genre, **dargs)
	text_type = models.ForeignKey(TextType, **dargs)
	# upload = models.FileField(upload_to='texts/',blank=True,null=True) # ?
	relations = models.ManyToManyField('self',
		through='TextTextRelation',symmetrical=False, default=None)
	location= models.ManyToManyField(Location,blank=True, default= None)
	description = models.TextField(blank=True)
	notes = models.TextField(default='',blank=True, null=True)
	complete = models.BooleanField(default=False)
	approved = models.BooleanField(default=False)
	source_link= models.CharField(max_length=1000,blank=True,null=True)
	copyright = models.ForeignKey(CopyRight,**dargs)
	location_field = 'location'

	def save(self):
		if not self.pk:
			self.text_id= id_generator(length = 27)
		super(Text, self).save()

	def __str__(self):
		return self.title

	@property
	def attribute_names(self):
		return 'title,language,genre,upload,notes'.split(',')

	@property
	def listify(self,date = '%Y'):
		m = []
		for attr in self.attribute_names:
			value = getattr(self,attr)
			if value == None: m.append('')
			else: m.append(value)
		return m

	@property
	def latlng(self):
		locations = field2locations(self,'location')
		if locations:
			return [location.gps for location in locations]
		else: return None

	@property
	def pop_up(self):
		return pop_up(self)	

	@property
	def instance_name(self):
		return self.title


class TextTextRelationType(models.Model, info):
	'''category of text2text relations e.g. a translation, review etc.'''
	name = models.CharField(max_length=100)
	notes= models.TextField(blank=True)

	def __str__(self):
		return self.name

	


class IllustrationCategory(models.Model):
	'''The type of illustration e.g painting.'''
	name = models.CharField(max_length=200,unique=True)
	notes = models.TextField(null=True,blank=True)
	
	def __str__(self):
		return self.name


class Illustration(models.Model, info):
	'''a illustration typically part of publication'''
	caption =  models.CharField(max_length=300,null=True,blank=True)
	category= models.ForeignKey(IllustrationCategory, on_delete=models.SET_NULL,
		blank=True,null=True, related_name='Illustration',)
	categories= models.ManyToManyField(IllustrationCategory, blank=True, related_name='Illustrations') 
	page_number = models.CharField(max_length=50, null=True, blank=True)
	notes = models.TextField(null=True,blank=True)
	description = models.TextField(blank=True)
	upload= models.ImageField(upload_to='illustrations/',null=True,blank=True)
	complete = models.BooleanField(default=False)
	approved = models.BooleanField(default=False)
	source_link= models.CharField(max_length=1000,blank=True,null=True)
	copyright = models.ForeignKey(CopyRight,on_delete=models.SET_NULL,blank=True,null=True)
	location_field = ''
	
	def __str__(self):
		return self.caption


	@property
	def latlng(self):
		return None

	@property
	def pop_up(self):
		return pop_up(self)	

	@property
	def instance_name(self):
		return self.caption

class Audience(models.Model, info): # only usefull for periodical not book?
	'''audience for a periodical'''
	name = models.CharField(max_length=100, null=True,blank=True)
	description = models.TextField(null=True,blank=True)

	def __str__(self):
		return self.name

class Book(models.Model, info):
	'''Redundant?'''
	title = models.CharField(max_length=300) 
	language = models.CharField(max_length=100,null=True,blank=True) 

	def __str__(self):
		return self.title
	

class Publisher(models.Model, info):
	'''Company that publishes works.'''
	name = models.CharField(max_length=300, unique=True)
	location= models.ManyToManyField(Location,blank=True,default=None)
	founded = models.PositiveIntegerField(null=True,blank=True) 
	closure = models.PositiveIntegerField(null=True,blank=True) 
	notes = models.TextField(null=True,blank=True) # many to many
	description = models.TextField(blank=True)
	complete = models.BooleanField(default=False)
	approved = models.BooleanField(default=False)
	location_field = 'location'

	def __str__(self):
		return self.name

	@property
	def location_string(self):
		return ', '.join([l.name for l in self.location.all()])

	@property
	def latlng(self):
		locations = field2locations(self,'location')
		if locations:
			return [location.gps for location in locations]
		else: return None

	@property
	def instance_name(self):
		return self.name

	class Meta:
		ordering = ['name']

	@property
	def pop_up(self):
		return pop_up(self)	


class PublicationType(models.Model):
	'''the type of pubilication eg. novel newspaper etc.'''
	name = models.CharField(max_length=100,unique=True)
	notes = models.TextField(null=True,blank=True) 

	def __str__(self):
		return self.name

class Publication(models.Model, info):
	'''The publication of a text or collection of texts and illustrations'''
	title = models.CharField(max_length=300,null=True)
	publisher = models.ManyToManyField(Publisher,blank=True)
	publication_id= models.CharField(max_length=30, default = '')
	form = models.ForeignKey(PublicationType,on_delete=models.SET_NULL,null=True)
	issue = models.PositiveIntegerField(null=True,blank=True) 
	volume = models.PositiveIntegerField(null=True,blank=True) 
	identifier = models.CharField(max_length=100,null=True,blank=True,unique=True) # not shown in form
	year = models.PositiveIntegerField(null=True,blank=True) # obsolete, replace by date
	date = PartialDateField(null=True,blank=True)
	location = models.ManyToManyField(Location,blank=True,default=None) 
	pdf = models.FileField(upload_to='publication/',null=True,blank=True) # ?
	cover = models.ImageField(upload_to='publication/',null=True,blank=True)
	complete = models.BooleanField(default=False)
	approved = models.BooleanField(default=False)
	notes = models.TextField(default='',blank=True, null=True)
	description = models.TextField(blank=True)
	source_link= models.CharField(max_length=1000,blank=True,null=True)
	copyright = models.ForeignKey(CopyRight,on_delete=models.SET_NULL,blank=True,null=True)
	location_field = 'location'

	def save(self):
		if not self.pk:
			self.publication_id= id_generator(length = 27)
		super(Publication, self).save()

	def __str__(self):
		return self.title # self.work.name

	@property
	def publisher_str(self):
		return ' | '.join([pu.name for pu in self.publisher.all()])

	@property
	def location_str(self):
		return ' | '.join([loc.name for loc in self.location.all()])

	@property
	def latlng(self):
		locations = field2locations(self,'location')
		if locations:
			return [location.gps for location in locations]
		else: return None

	@property
	def pop_up(self):
		return pop_up(self)	

	@property
	def instance_name(self):
		return self.title

class TextPublicationRelation(RelationModel): #many to many
	'''Links a text with a publication.'''
	text = models.ForeignKey(Text, on_delete=models.CASCADE)
	publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
	start_page = models.CharField(max_length=5,null=True,blank=True)
	end_page = models.CharField(max_length=5,null=True,blank=True)
	model_fields = ['text','publication']

	def __str__(self):
		m =  self.text.title+ ' is a part of '
		m += self.publication.title
		return m

	@property
	def primary(self):
		return self.text
		

class TextReviewPublicationRelation(RelationModel): #many to many
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

class IllustrationPublicationRelation(RelationModel): #many to many
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

class Periodical(models.Model, info):
	'''Recurrent publication.'''
	title = models.CharField(max_length=300)
	founded = models.PositiveIntegerField(null=True,blank=True) 
	closure = models.PositiveIntegerField(null=True,blank=True) 
	location= models.ManyToManyField(Location,blank=True,default =None)
	complete = models.BooleanField(default=False)
	approved = models.BooleanField(default=False)
	location_field = 'location'
	description = models.TextField(blank=True)

	def __str__(self):
		return self.title

	@property
	def location_str(self):
		return 

	@property
	def latlng(self):
		locations = field2locations(self,'location')
		if locations:
			return [location.gps for location in locations]
		else: return None

	@property
	def instance_name(self):
		return self.title

	@property
	def pop_up(self):
		return pop_up(self)	

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

	
