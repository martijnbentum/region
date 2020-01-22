from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
# from django_countries.fields import CountryField
# from .util_models import info
# from .util_models import id_generator
import json
from locations.models import UserLoc
from utils.model_util import id_generator, info


class Date(models.Model, info):
	start= models.DateField(blank = True, null = True)
	end= models.DateField(blank = True, null = True)
	SPECIFICITY = [('d','day'),('m','month'),('y','year'),('c','century')]
	start_specificity=models.CharField(max_length=1,choices=SPECIFICITY,default='d')
	end_specificity=models.CharField(max_length=1,choices=SPECIFICITY,default='d') 

	@property
	def attribute_names(self):
		return 'start,end,start_specificity,end_specificity'.split(',')

	def _set_specificity_str(self):
		if self.start_specificity == 'd': self.start_strf = '%-d %B %Y'
		elif self.start_specificity == 'm': self.start_strf = '%B %Y'
		elif self.start_specificity in ['y','c']: self.start_strf = '%Y'
		if self.end_specificity == 'd': self.end_strf = '%-d %B %Y'
		if self.end_specificity == 'm': self.end_strf = '%B %Y'
		if self.end_specificity in ['y','c']: self.end_strf = '%Y'

	def	_set_time_delta(self):
		if self.start and self.end:
			self.delta = self.end - self.start
		elif self.start:
			self.delta = timezone.datetime.date(timezone.now()) - self.start
		else: self.delta = None

	@property
	def start_str(self):
		self._set_specificity_str()
		if self.start: return self.start.strftime(self.start_strf) 
		return ''
		
	@property
	def end_str(self):
		self._set_specificity_str()
		if self.end: return self.end.strftime(self.end_strf) 
		return ''

	@property
	def duration_str(self):
		self._set_specificity_str()
		if self.start and self.end: t = (self.end.year - self.start.year)
		elif self.start:
			t = timezone.datetime.date(timezone.now()).year - self.start.year
		else: return ''
		if t == 1 and self.delta.days >= 365: t = str(t) + ' year'
		elif t > 1: t = str(t) + ' years'
		elif spec == ['d','d']: 
			t = str(self.delta.days) + ' day'
			if self.delta.days > 1: t += 's'
		return t

	def list(self):
		self._set_specificity_str()
		self._set_time_delta()
		m = []
		if self.start: m.append( self.start_str )
		if self.end: m.append( self.end_str )
		spec = [self.start_specificity,self.end_specificity]
		if 'c' in spec or not self.delta: return m
		t = self.duration_str
		if type(t) == str and t != '': m.append(t)
		return m

	def __str__(self):
		m = ''
		if not self.ok(): m += self.error
		for n,v in zip('start,end,duration'.split(','), self.list()):
			m += n + ': ' + v + '   '
		return m.rstrip('   ')

	def ok(self):
		self.error = ''
		self._set_time_delta()
		if self.start and self.end:	
			if self.delta.days < 0: self.error = 'end date before start date '
			return self.delta.days >= 0
		if not self.start:
			self.error = 'no start date '
		if not self.start and not self.end:
			self.error = 'no dates '
			

class Person(models.Model, info):
	'''A person with a specific role e.g. author, writer, etc.'''
	first_name = models.CharField(max_length=200)
	last_name = models.CharField(max_length=200)
	SEX = [('F','female'),('M','male'),('O','other')]
	sex = models.CharField(max_length=1,choices=SEX)
	birth_death_date = models.ForeignKey(Date, 
		on_delete=models.SET_NULL,default=None,null =True)
	place_of_birth = models.ForeignKey(UserLoc, on_delete=models.SET_NULL,
		related_name = 'born', default = None, null = True)
	place_of_death= models.ForeignKey(UserLoc, on_delete=models.SET_NULL,
		related_name = 'died', default = None, null = True)
	notes = models.TextField(blank=True,null=True) 


	@property
	def name(self):
		return self.first_name + ' ' + self.last_name
	
	def __str__(self):
		return self.name

	@property
	def born(self):
		return self.birth_death_date.start_str

	@property
	def died(self):
		return self.birth_death_date.end_str

	@property
	def age(self):
		return self.birth_death_date.duration_str


	@property
	def attribute_names(self):
		m = 'first_name,last_name,sex,birth_death_date,place_of_birth'
		m += ',place_of_death,notes'
		return m.split(',')

	@property
	def locations(self):
		locs, names = [], []
		for n in 'place_of_birth,place_of_death'.split(','):
			if getattr(self,n):
				locs.append(getattr(self,n))
				names.append(n.replace('_',' '))
		for plr in self.personlocationrelation_set.all():
			locs.append(plr.location)
			names.append(plr.relation_name)
		return locs, names

	@property
	def location_status(self):
		locs, names = self.locations
		o = dict([[str(i),n] for i,n in zip(range(1,len(names)+1),names)])
		# return ','.join(names)
		return json.dumps(o)

	@property
	def listify(self,date = '%Y'):
		m = []
		for attr in self.attribute_names:
			value = getattr(self,attr) 
			if attr == 'sex': m.append(dict(self.SEX)[self.sex])
			elif 'date_of' in attr: 
				try:m.append(getattr(self,attr).strftime(date))
				except: m.append('')
			elif value == None: m.append('')
			else: m.append(str(getattr(self,attr)))
		return m

	@property
	def table_header(self):
		return 'name,age,sex,born,died,birthplace,deathplace'.split(',')

	@property
	def table(self):
		return [self.name,self.age,sex,born,died,birthplace,deathplace]


class Pseudonym(models.Model, info):
	person = models.ForeignKey(Person, related_name='Pseudonyms', 
		on_delete=models.CASCADE)
	name = models.CharField(max_length=500)

class PersonLocationRelation(models.Model,info):
	'''location function for a person e.g. residence, work, travel.'''
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	location = models.ForeignKey(UserLoc, on_delete=models.CASCADE)
	RELATION= [('R','residence'),('T','travel'),('W','work'),('U','unknown')]
	relation= models.CharField(max_length=1,choices= RELATION,default = None)
	date = models.ForeignKey(Date, default= None, on_delete=models.CASCADE)
	location_name = models.CharField(max_length=200, default='',null=True)
	person_name = models.CharField(max_length=200, default='',null=True)

	@property
	def relation_name(self):
		return dict(self.RELATION)[self.relation]

	def __str__(self):
		r = self.relation_name
		return ', '.join([self.person.name, self.location.name, r])

	@classmethod
	def create(cls):
		if hasattr(cls,'location'):
			cls.location_name = cls.location.name
		if hasattr(cls,'person'):
			cls.person_name = cls.person.first_name + ' ' + cls.person.last_name



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
	location= models.ManyToManyField(UserLoc)
	start_end_date = models.ForeignKey(Date,null=True,on_delete=models.SET_NULL)
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
	location = models.ForeignKey(UserLoc, on_delete=models.SET_NULL,null=True)
	e_text = models.FileField(upload_to='publication/') # ?

	def __str__(self):
		return 'work_name' # self.work.name

class WorkPublicationRelation(models.Model): #many to many
	'''Links a work with a publication.'''
	work = '' # FK text | FK illustration
	publication = models.ForeignKey(Publication, on_delete=models.CASCADE)












	
