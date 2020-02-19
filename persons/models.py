from django.db import models
from django.utils import timezone
import json
from locations.models import UserLoc
from utilities.models import Language
from utils.model_util import id_generator, info




class Pseudonym(models.Model, info):
	name = models.CharField(max_length=300, unique= True)

	def __str__(self):
		return self.name

class Function(models.Model, info): 
	name = models.CharField(max_length=200, unique=True)
	
	def __str__(self):
		return self.name

class Person(models.Model, info):
	'''A person with a specific role e.g. author, writer, etc.'''
	first_name = models.CharField(max_length=200)
	last_name = models.CharField(max_length=200)
	SEX = [('F','female'),('M','male'),('O','other')]
	sex = models.CharField(max_length=1,choices=SEX)
	function= models.ManyToManyField(Function,blank=True)
	pseudonym= models.ManyToManyField(Pseudonym,blank=True)
	birth_year = models.PositiveIntegerField(null=True,blank=True)
	death_year = models.PositiveIntegerField(null=True,blank=True)
	birth_place= models.ForeignKey(UserLoc, on_delete=models.SET_NULL,
		related_name = 'born', default = None, null = True)
	death_place= models.ForeignKey(UserLoc, on_delete=models.SET_NULL,
		related_name = 'died', default = None, null = True)
	notes = models.TextField(blank=True,null=True) 

	@property
	def name(self):
		return self.first_name + ' ' + self.last_name
	
	def __str__(self):
		return self.name

	@property
	def born(self):
		return self.birth_year

	@property
	def died(self):
		return self.death_year

	@property
	def attribute_names(self):
		m = 'first_name,last_name,sex,birth_year,death_year,birth_place'
		m += ',death_place,notes'
		return m.split(',')

	@property
	def locations(self):
		locs, names = [], []
		for n in 'birth_place,death_place'.split(','):
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
		return 'name,sex,born,died,birth_place,death_place'.split(',')

	@property
	def table(self):
		return [self.name,self.age,sex,born,died,birthplace,deathplace]




class LocationRelation(models.Model, info):
	name = models.CharField(max_length=200,unique=True)
	notes = models.TextField(null=True,blank=True)

	def __str__(self):
		return self.name

class PersonLocationRelation(models.Model,info):
	'''location function for a person e.g. residence, work, travel.'''
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	location = models.ForeignKey(UserLoc, on_delete=models.CASCADE)
	# RELATION= [('R','residence'),('T','travel'),('W','work'),('U','unknown')]
	# relation= models.CharField(max_length=1,choices= RELATION,null= None)
	relation = models.ForeignKey(LocationRelation, null=True, on_delete=models.SET_NULL)
	start_year = models.PositiveIntegerField(null=True,blank=True)
	end_year = models.PositiveIntegerField(null=True,blank=True)
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



class PersonTextRelationRole(models.Model, info):
	'''e.g author | translator | editor | subject | ... '''
	# how to initialize with above values
	name = models.CharField(max_length = 100,unique=True)
	notes = models.TextField(null=True,blank=True)

	def __str__(self):
		return self.name


class PersonIllustrationRelationRole(models.Model, info):
	'''e.g illustrator | subject | ... '''
	# how to initialize with above values
	name = models.CharField(max_length = 100,unique=True)
	notes = models.TextField(null=True,blank=True)

	def __str__(self):
		return self.name


class PublisherManager(models.Model): #or broker
	'''Person that manages writers, should be linked to texts and creators?'''
	# Publisher= apps.get_model('catalogue','Publisher')
	publisher = models.ForeignKey('catalogue.Publisher', 
		on_delete=models.CASCADE, related_name='publisher')
	manager = models.ForeignKey(Person, on_delete=models.CASCADE,
		related_name='manager')


class PersonTextRelation(models.Model, info):
	role = models.ForeignKey(PersonTextRelationRole, on_delete=models.CASCADE)
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	text = models.ForeignKey('catalogue.Text', null=True, blank=True, 
		on_delete=models.CASCADE)
	
	def __str__(self):
		m = self.person.__str__() + ' | ' + self.role.__str__() 
		m += ' | ' + self.text.__str__()
		return m

	class Meta:
		unique_together = ['role','person','text']


class PersonIllustrationRelation(models.Model, info):
	role = models.ForeignKey(PersonIllustrationRelationRole, 
		on_delete=models.CASCADE)
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	illustration= models.ForeignKey('catalogue.Illustration', null=True, 
		blank=True, on_delete=models.CASCADE)
	
	def __str__(self):
		m = self.person.__str__() + ' | ' + self.role.__str__() 
		m += ' | ' + self.illustration.__str__()
		return m

	class Meta:
		unique_together = ['role','person','illustration']


# Create your models here.
