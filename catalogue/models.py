from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# from django_countries.fields import CountryField
from .util_models import info
from .util_models import id_generator


class Date(models.Model):
	start_date = models.DateField()
	end_date = models.DateField()
	DATE_SPEC = [('d','day'),('m','month'),('y','year'),('c','century')]
	start_spec = models.CharField(max_length=1,choices=DATE_SPEC,default='d')
	end_spec = models.CharField(max_length=1,choices=DATE_SPEC,default='d')

class Location(models.Model, info):
	'''Geographic location of a specific type (e.g. city or country)'''
	name = models.CharField(max_length=200, default = '')
	FICTION = 'F'
	NON_FICTION = 'NF'
	STATUS = [(FICTION,'fiction'), (NON_FICTION,'non-fiction')]
	status = models.CharField(max_length=2,choices=STATUS,default = 'NF')
	CITY = 'CIT'
	PROVINCE = 'PRO'
	COUNTRY = 'COU'
	CONTINENT = 'CON'
	REGION = 'REG'
	LOCATION_TYPE = [
		(CITY,'city'),
		(PROVINCE,'province'),
		(COUNTRY,'country'),
		(CONTINENT,'continent'),
		(REGION,'region'),
	]
	location_type= models.CharField(
		max_length=3,
		choices=LOCATION_TYPE,
		default = CITY
	)
	relations = models.ManyToManyField('self',
		through='LocationLocationRelation',symmetrical=False, default=None)
	geonameid = models.CharField(
		max_length=12, 
		default= id_generator(length = 12),
		unique = True,
	)
	coordinates_polygon = models.CharField(max_length=3000, blank=True ,null=True)
	latitude=models.DecimalField(
		blank=True,
		null=True,
		max_digits=8,
		decimal_places=5
	)
	longitude=models.DecimalField(
		blank=True,
		null=True,
		max_digits=8,
		decimal_places=5
	)
	notes = models.TextField(default='',blank=True)
	# country = CountryField()

	def __str__(self):
		return self.name 

	@property
	def attribute_names_hr(self):
		names = 'name,status,type,notes'.split(',')
		return names

	@property
	def listify(self):
		names = 'name,status,location_type,notes'.split(',')
		m = []
		for attr in names:
			if attr == 'status': m.append(dict(self.STATUS)[self.status])
			elif attr == 'location_type': 
				m.append(dict(self.LOCATION_TYPE)[self.location_type])
			elif attr == 'notes':  
				note =  getattr(self,attr) 
				m.append('') if note == None else m.append(note)
			else: m.append(str(getattr(self,attr)))
		return m
	
	class Meta:
		ordering = ['name']


class LocationLocationRelation(models.Model, info):
	'''defines a hierarchy of locations, e.g. a city is in a province.'''
	container = models.ForeignKey('Location', related_name='container',
									on_delete=models.CASCADE, default=None)
	contained = models.ForeignKey('Location', related_name='contained',
									on_delete=models.CASCADE, default=None)

	def __str__(self):
		return self.contained.name + ' is located in: ' + self.container.name
	

class Person(models.Model, info):
	'''A person with a specific role e.g. author, writer, etc.'''
	first_name = models.CharField(max_length=200)
	last_name = models.CharField(max_length=200)
	GENDER = [('F','female'),('M','male'),('O','other')]
	gender = models.CharField(max_length=1,choices=GENDER)
	notes = models.TextField(blank=True,null=True) # one to many
	
	def __str__(self):
		return self.first_name + ' ' + self.last_name

	@property
	def attribute_names(self):
		m = 'first_name,last_name,gender'
		m += ',notes'
		return m.split(',')

	@property
	def attribute_names_hr(self):
		m = ','.join(self.attribute_names)
		m = m.replace('date_of_birth','born')
		m = m.replace('date_of_death','died')
		m = m.replace('date_spec','date specificity')
		m = m.replace('_',' ')
		return m.split(',')

	@property
	def listify(self,date = '%Y'):
		m = []
		for attr in self.attribute_names:
			value = getattr(self,attr) 
			if attr == 'gender': m.append(dict(self.GENDER)[self.gender])
			elif 'date_of' in attr: 
				try:m.append(getattr(self,attr).strftime(date))
				except: m.append('')
			elif value == None: m.append('')
			else: m.append(str(getattr(self,attr)))
		return m


class Pseudonym(models.Model, info):
	person = models.ForeignKey(Person, related_name='Pseudonyms', 
		on_delete=models.CASCADE)
	name = models.CharField(max_length=500)

class PersonLocationRelation(models.Model):
	'''location function for a person e.g. residence, work, travel.'''
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	location = models.ForeignKey(Location, on_delete=models.CASCADE)
	#hard coded location function good idea?
	RELATION= [('R','residence'),('T','travel'),('B','birth'),
		('D','death'),('W','work'),('U','unknown')]
	relation= models.CharField(max_length=1,choices= RELATION,default = None)
	date = models.ForeignKey(Date, default= None, on_delete=models.CASCADE)




class Genre(models.Model, info):
	'''category for texts (and maybe illustrations?) needs a relation as well?L'''
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	
	def __str__(self):
		return self.name


class Language(models.Model, info):
	name = models.CharField(max_length=100)
	iso = models.CharField(max_length=3,null=True,blank=True)

	def __str__(self):
		return self.name

class Text(models.Model, info):
	'''a text can be an entire book or article or a subsection thereof.'''
	title = models.CharField(max_length=300)
	language = models.ForeignKey(Language, on_delete=models.CASCADE)
	genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
	upload = models.FileField(upload_to='texts/',blank=True,null=True) # ?
	relations = models.ManyToManyField('self',
		through='TextTextRelation',symmetrical=False, default=None)
	notes = models.TextField(default='',blank=True)

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
	language = models.CharField(max_length=100,null=True,blank=True)
	context = models.TextField(null=True,blank=True)
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
	'''Recurrent publication.'''
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
	'''Company that publishes works.'''
	name = models.CharField(max_length=300)
	location= models.ManyToManyField(Location,blank=True)
	start_date = models.DateField(null=True,blank=True)
	end_date = models.DateField(null=True,blank=True)
	notes = models.TextField(null=True,blank=True) # many to many

	def __str__(self):
		return self.name
	
class PublisherManager(models.Model): #or broker
	'''Person that manages writers, should be linked to texts and creators?'''
	publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
	manager = models.ForeignKey(Person, on_delete=models.CASCADE)

class Publication(models.Model, info):
	'''A specific instance of a text and or illustration or periodical or book?'''
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
	'''Links a work with a publication.'''
	work = '' # FK text | FK illustration
	publication = models.ForeignKey(Publication, on_delete=models.CASCADE)












	
