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
	pseudonyms = models.CharField(max_length=200,blank=True,null=True) 
	GENDER = [('F','female'),('M','male'),('O','other')]
	gender = models.CharField(max_length=1,choices=GENDER)
	date_of_birth = models.DateField(blank=True,null=True)
	date_of_death = models.DateField(blank=True,null=True)
	residence = models.ForeignKey(Location, on_delete=models.CASCADE) # multiple residences?? duplicate of PersonLocationRelation??
	notes = models.TextField(blank=True,null=True) # one to many
	
	def __str__(self):
		return self.first_name + ' ' + self.last_name

class PersonLocationRelation(models.Model):
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	location = models.ForeignKey(Location, on_delete=models.CASCADE)
	LOCATION_TYPE = [('R','residence'),('T','travel')]
	location_type = models.CharField(max_length=1,choices=LOCATION_TYPE)
	start_date = models.DateField()
	end_date = models.DateField()



class Genre(models.Model, info):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	
	def __str__(self):
		return self.name

class Text(models.Model, info):
	title = models.CharField(max_length=300)
	language = models.CharField(max_length=100)
	genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
	upload = models.FileField(upload_to='texts/',blank=True,null=True) # ?
	relations = models.ManyToManyField('self',
		through='TextTextRelation',symmetrical=False, default=None)
	notes = models.TextField(default='',blank=True)

	def __str__(self):
		return self.title

class TextTextRelationType(models.Model, info):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)

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
	'''What is the function of fragment'''
	#fk text
	#contents
	pass



class Illustration(models.Model, info):
	caption =  models.CharField(max_length=300,null=True,blank=True)
	language = models.CharField(max_length=100,null=True,blank=True)
	context = models.TextField(null=True,blank=True)
	illustration_format = '' # ... | ...
	upload = models.ImageField(upload_to='illustrations/',null=True,blank=True)
	
	def __str__(self):
		return self.caption

class IllustrationCategory(models.Model):
	category = models.CharField(max_length=100)
	description = models.TextField(null=True,blank=True)

class IllustrationCategoryRelation(models.Model): # many to many
	illustration = models.ForeignKey(Illustration, on_delete=models.CASCADE)
	category = models.ForeignKey(IllustrationCategory, on_delete=models.CASCADE)



class PersonWorkRelationRole(models.Model, info):
	'''e.g author | illustrator | translator | editor | subject | ... '''
	# how to initialize with above values
	role = models.CharField(max_length = 100)
	description = models.TextField(null=True,blank=True)

	def __str__(self):
		return self.role

class PersonWorkRelation(models.Model, info):
	role = models.ForeignKey(PersonWorkRelationRole, on_delete=models.CASCADE)
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	# unique together [person, role]
	main_creator = models.BooleanField()
	work_text = models.ForeignKey(Text, null=True, blank=True, 
									on_delete=models.CASCADE)
	work_illustration= models.ForeignKey(Illustration, null=True, blank=True,
									on_delete=models.CASCADE)
	
	def __str__(self):
		m = self.person.__str__() + ' | ' + self.role.__str__() 
		m += ' | ' + self.work.__str__()
		return m

	@property
	def work(self):
		if self.work_text is not None:
			return self.work_text
		if self.work_illustration is not None:
			return self.work_illustration
		raise AssertionError("neither (work) text nor illustration is set")

	def save(self,*args, **kwargs):
		if ((self.work_text == self.work_illustration == None) or
			(self.work_text != None and self.work_illustration != None)):
			raise AssertionError('set either (work) text or illustration')
		super(PersonWorkRelation, self).save(*args, **kwargs)
		


class Periodical(models.Model, info):
	title = models.CharField(max_length=300)
	language = models.CharField(max_length=100)
	start_date = models.DateField()
	end_date = models.DateField()
	location = models.ForeignKey(Location, on_delete=models.CASCADE)

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
	name = models.CharField(max_length=300)
	location= models.ManyToManyField(Location,blank=True)
	start_date = models.DateField(null=True,blank=True)
	end_date = models.DateField(null=True,blank=True)
	notes = models.TextField(null=True,blank=True) # many to many

	def __str__(self):
		return self.name
	
class PublisherManager(models.Model): #or broker
	publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
	manager = models.ForeignKey(Person, on_delete=models.CASCADE)

class Publication(models.Model, info):
	publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
	form = '' # FK periodical | FK book
	issue = models.PositiveIntegerField(null=True,blank=True) 
	volume = models.PositiveIntegerField(null=True,blank=True) 
	identifier = models.CharField(max_length=100,null=True,blank=True)# ISBN
	date = models.DateField(null=True,blank=True)
	location = models.ForeignKey(Location, on_delete=models.CASCADE)
	e_text = models.FileField(upload_to='publication/') # ?

	def __str__(self):
		return 'work_name' # self.work.name

class WorkPublicationRelation(models.Model): #many to many
	work = '' # FK text | FK illustration
	publication = models.ForeignKey(Publication, on_delete=models.CASCADE)












	
