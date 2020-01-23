from django.db import models
from django.utils import timezone
import json
from locations.models import UserLoc
from utilities.models import Date, Language
from utils.model_util import id_generator, info


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


class Pseudonym(models.Model, info):
	person = models.ForeignKey(Person, related_name='Pseudonyms', 
		on_delete=models.CASCADE)
	name = models.CharField(max_length=500)



# Create your models here.
