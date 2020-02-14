from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import json
from locations.models import UserLoc
from persons.models import Person
from utilities.models import Date, Language
from utils.model_util import id_generator, info
			

class Genre(models.Model, info):
	'''category for texts (and maybe illustrations?) needs a relation as well?'''
	name = models.CharField(max_length=100,unique=True)
	description = models.TextField(blank=True)
	
	def __str__(self):
		return self.name


class Text(models.Model, info):
	'''a text can be an entire book or article or a subsection thereof.'''
	title = models.CharField(max_length=300)
	text_id = models.IntegerField(default = id_generator('numbers',length=12),
		unique = True)
	setting = models.CharField(max_length=300,blank=True)
		
	language = models.ForeignKey(Language, on_delete=models.SET_NULL,
		blank=True,null=True)
	genre = models.ForeignKey(Genre, on_delete=models.SET_NULL,
		blank=True,null=True)
	upload = models.FileField(upload_to='texts/',blank=True,null=True) # ?
	relations = models.ManyToManyField('self',
		through='TextTextRelation',symmetrical=False, default=None)
	notes = models.TextField(default='',blank=True, null=True)

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


class TextTextRelationType(models.Model, info):
	'''category of text2text relations e.g. a translation, review etc.'''
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)

	def __str__(self):
		return self.name
	
class TextTextRelation(models.Model, info):
	'''connects two texts with a specific type of relation e.g. original 
	and translation (primary, secondary).'''
	primary = models.ForeignKey('Text', related_name='primary',
									on_delete=models.CASCADE, default=None)
	secondary = models.ForeignKey('Text', related_name='secondary',
									on_delete=models.CASCADE, default=None)
	relation_type = models.ForeignKey(TextTextRelationType, 
									on_delete=models.CASCADE, default=None)

	def __str__(self):
		m =  self.secondary.name + ' is a ' + self.relation_type.name +' of '
		m += self.primary.name
		return m


class Fragment(models.Model):
	'''What is the function of fragment, could be a binary flag on text'''
	#fk text
	#contents
	pass


class Illustration(models.Model, info):
	'''a picture, should the picture itself be saveable?, illustration format?'''
	caption =  models.CharField(max_length=300,null=True,blank=True)
	page_number = models.PositiveIntegerField(null=True,blank=True)
	notes = models.TextField(null=True,blank=True)
	illustration_format = '' # ... | ...
	upload = models.ImageField(upload_to='illustrations/',null=True,blank=True)
	
	def __str__(self):
		return self.caption

class IllustrationCategory(models.Model):
	'''could also be genre?'''
	category = models.CharField(max_length=100)
	description = models.TextField(null=True,blank=True)

class IllustrationCategoryRelation(models.Model): # many to many
	'''links a category to an illustration.'''
	illustration = models.ForeignKey(Illustration, on_delete=models.CASCADE)
	category = models.ForeignKey(IllustrationCategory, on_delete=models.CASCADE)


class Periodical(models.Model, info):
	'''Recurrent publication.'''
	title = models.CharField(max_length=300)
	language = models.CharField(max_length=100)
	start_date = models.DateField()
	end_date = models.DateField()
	location = models.ForeignKey(UserLoc, null=True,on_delete=models.SET_NULL)

	def __str__(self):
		return self.title

class Audience(models.Model, info): # only usefull for periodical not book?
	name = models.CharField(max_length=100, null=True,blank=True)
	description = models.TextField(null=True,blank=True)

	def __str__(self):
		return self.name

class Book(models.Model, info):
	title = models.CharField(max_length=300) 
	language = models.CharField(max_length=100,null=True,blank=True) 

	def __str__(self):
		return self.title
	

class Publisher(models.Model, info):
	'''Company that publishes works.'''
	name = models.CharField(max_length=300)
	location= models.ManyToManyField(UserLoc,blank=True)
	start_end_date = models.ForeignKey(Date,blank= True,null=True,
		on_delete=models.SET_NULL)
	notes = models.TextField(null=True,blank=True) # many to many

	def __str__(self):
		return self.name

	@property
	def location_string(self):
		return ', '.join([l.name for l in self.location.all()])

class PublisherManager(models.Model): #or broker
	'''Person that manages writers, should be linked to texts and creators?'''
	publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
	manager = models.ForeignKey(Person, on_delete=models.CASCADE)

class Type(models.Model):
	name = models.CharField(max_length=100,unique=True)
	notes = models.TextField(null=True,blank=True) 

	def __str__(self):
		return self.name

class Publication(models.Model, info):
	'''The publication of a text or collection of texts and illustrations'''
	title = models.CharField(max_length=300,null=True)
	publisher = models.ManyToManyField(Publisher,blank=True)
	publication_id = models.IntegerField(
		default = id_generator('numbers',length=12), unique= True)
	form = models.ForeignKey(Type,on_delete=models.SET_NULL,null=True) 
	# FK periodical | FK book
	issue = models.PositiveIntegerField(null=True,blank=True) 
	volume = models.PositiveIntegerField(null=True,blank=True) 
	identifier = models.CharField(max_length=100,null=True,blank=True,unique=True)
	# ISBN
	year = models.PositiveIntegerField(null=True,blank=True)
	location = models.ManyToManyField(UserLoc,blank=True) 
	upload = models.FileField(upload_to='publication/',null=True,blank=True) # ?

	def __str__(self):
		return self.title # self.work.name

	@property
	def publisher_str(self):
		return ' | '.join([pu.name for pu in self.publisher.all()])

class TextPublicationRelation(models.Model): #many to many
	'''Links a work with a publication.'''
	text = models.ForeignKey(Text, on_delete=models.CASCADE)
	publication = models.ForeignKey(Publication, on_delete=models.CASCADE)

class IllustrationPublicationRelation(models.Model): #many to many
	'''Links a work with a publication.'''
	text = models.ForeignKey(Illustration, on_delete=models.CASCADE)
	publication = models.ForeignKey(Publication, on_delete=models.CASCADE)












	
