from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# from django_countries.fields import CountryField
from .util import info



class LocationType(models.Model, info):
	name = models.CharField(max_length=100, default = None)
	description = models.TextField(default ='',blank=True)

	def __str__(self):
		return self.name

class Location(models.Model, info):
	name = models.CharField(max_length=200, default = '')
	STATUS = [('F','fiction'), ('NF','non-fiction')]
	status = models.CharField(max_length=2,choices=STATUS,default = 'NF')
	location_type = models.ForeignKey(LocationType,on_delete=models.CASCADE,
										default = None)
	relations = models.ManyToManyField('self',
		through='LocationLocationRelation',symmetrical=False, default=None)
	notes = models.TextField(default='',blank=True)
	# country = CountryField()

	def __str__(self):
		return self.name 



class LocationLocationRelation(models.Model, info):
	container = models.ForeignKey('Location', related_name='container',
									on_delete=models.CASCADE, default=None)
	contained = models.ForeignKey('Location', related_name='contained',
									on_delete=models.CASCADE, default=None)

	def __str__(self):
		return self.contained.name + ' is located in: ' + self.container.name
	

class Person(models.Model, info):
	first_name = models.CharField(max_length=200)
	last_name = models.CharField(max_length=200)
	pseudonyms = models.CharField(max_length=200) #one to many
	GENDER = [('F','female'),('M','male'),('O','other')]
	gender = models.CharField(max_length=1,choices=GENDER)
	date_of_birth = models.DateField()
	date_of_death = models.DateField()
	residence = models.ForeignKey(Location, on_delete=models.CASCADE) # multiple residences?? duplicate of PersonLocationRelation??
	notes = models.TextField() # one to many
	
	def __str__(self):
		return self.first_name + ' ' + self.last_name


class PersonLocationRelation(models.Model):
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	location = models.ForeignKey(Location, on_delete=models.CASCADE)
	LOCATION_TYPE = [('R','residence'),('T','travel')]
	location_type = models.CharField(max_length=1,choices=LOCATION_TYPE)
	start_date = models.DateField()
	end_date = models.DateField()


class PersonWorkRelationRole(models.Model, info):
	'''e.g author | illustrator | translator | editor | subject | ... '''
	# how to initialize with above values
	role = models.CharField(max_length = 100)
	description = models.TextField()

	def __str__(self):
		return self.role


class PersonWorkRelation(models.Model, info):
	role = models.ForeignKey(PersonWorkRelationRole, on_delete=models.CASCADE)
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	# unique together [person, role]
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
									default = None)
	object_id = models.PositiveIntegerField(default= None)
	work = GenericForeignKey('content_type','object_id') # FK text | FK illustration
	main_creator = models.BooleanField()
	
	def __str__(self):
		return self.person.__str__() + ' ' + self.role.__str__()

class Genre(models.Model, info):
	name = models.CharField(max_length=100)
	description = models.TextField()
	
	def __str__(self):
		return self.name

class Text(models.Model, info):
	title = models.CharField(max_length=300)
	language = models.CharField(max_length=100)
	genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
	upload = models.FileField(upload_to='texts/') # ?
	relations = models.ManyToManyField('self',
		through='TextTextRelation',symmetrical=False, default=None)
	notes = models.TextField(default='',blank=True)

	def __str__(self):
		return self.title

class TextTextRelationType(models.Model, info):
	name = models.CharField(max_length=100)
	description = models.TextField()

	def __str__(self):
		return self.name
	
class TextTextRelation(models.Model, info):
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
	pass

class Illustration(models.Model, info):
	caption =  models.CharField(max_length=300)
	language = models.CharField(max_length=100)
	context = models.TextField()
	illustration_format = '' # ... | ...
	upload = models.ImageField(upload_to='illustrations/') # ?
	
	def __str__(self):
		return self.caption

class IllustrationCategory(models.Model):
	category = models.CharField(max_length=100)
	description = models.TextField()

class IllustrationCategoryRelation(models.Model): # many to many
	illustration = models.ForeignKey(Illustration, on_delete=models.CASCADE)
	category = models.ForeignKey(IllustrationCategory, on_delete=models.CASCADE)




class Periodical(models.Model, info):
	title = models.CharField(max_length=300)
	language = models.CharField(max_length=100)
	start_date = models.DateField()
	end_date = models.DateField()
	location = models.ForeignKey(Location, on_delete=models.CASCADE)

	def __str__(self):
		return self.title

class Audience(models.Model, info): # only usefull for periodical not book?
	name = models.CharField(max_length=100)
	description = models.TextField()

	def __str__(self):
		return self.name


class Book(models.Model, info):
	title = models.CharField(max_length=300) # duplicate -> text
	language = models.CharField(max_length=100) # duplicate -> text

	def __str__(self):
		return self.title
	
class Publisher(models.Model, info):
	name = models.CharField(max_length=300)
	start_date = models.DateField()
	end_date = models.DateField()
	notes = models.TextField() # many to many

	def __str__(self):
		return self.name
	

class PublisherLocationRelation(models.Model):
	publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
	location = models.ForeignKey(Location, on_delete=models.CASCADE)

class PublisherManager(models.Model): #or broker
	publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
	manager = models.ForeignKey(Person, on_delete=models.CASCADE)


class Publication(models.Model, info):
	publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
	form = '' # FK periodical | FK book
	issue = models.PositiveIntegerField() # should this be on periodical?
	volume = models.PositiveIntegerField() # should this be on periodical?
	identifier = ''# ISBN
	date = models.DateField()
	location = models.ForeignKey(Location, on_delete=models.CASCADE)
	e_text = models.FileField(upload_to='publication/') # ?

	def __str__(self):
		return 'work_name' # self.work.name

class WorkPublicationRelation(models.Model): #many to many
	work = '' # FK text | FK illustration
	publication = models.ForeignKey(Publication, on_delete=models.CASCADE)












	
