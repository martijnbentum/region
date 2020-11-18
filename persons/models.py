from django.db import models
from django.utils import timezone
import json
from locations.models import Location
from utilities.models import Language, RelationModel
from utils.model_util import id_generator, info
from utils.map_util import field2locations, pop_up
from utilities.models import SimpleModel


def make_simple_model(name):
	exec('class '+name + '(SimpleModel):\n\tpass',globals())

names = 'Pseudonym,PersonPersonRelationType,PersonLocationRelationType,PersonTextRelationRole'
names += ',PersonIllustrationRelationRole,MovementType,PersonPeriodicalRelationRole'
names += ',PersonMovementRelationRole'
names = names.split(',')

for name in names:
	make_simple_model(name)




# --- main models ---

class Person(models.Model, info):
	'''A person with a specific role e.g. author, writer, etc.'''
	dargs = {'on_delete':models.SET_NULL,'default':None,'null':True}
	first_name = models.CharField(max_length=200, null=True, blank=True)
	last_name = models.CharField(max_length=200, null=True, blank=True)
	SEX = [('female','female'),('male','male'),('other','other'),('unknown','unknown')]
	sex = models.CharField(max_length=15,choices=SEX)
	pseudonym= models.ManyToManyField(Pseudonym,blank=True)
	birth_year = models.PositiveIntegerField(null=True,blank=True)
	death_year = models.PositiveIntegerField(null=True,blank=True)
	birth_place= models.ForeignKey(Location, related_name = 'hborn', **dargs)
	death_place= models.ForeignKey(Location, related_name = 'hdied', **dargs)
	notes = models.TextField(blank=True,null=True) 
	description = models.TextField(blank=True)
	complete = models.BooleanField(default=False)
	approved = models.BooleanField(default=False)
	location_field = 'birth_place'

	@property
	def name(self):
		if self.first_name == None: return self.last_name
		if self.last_name == None: return self.first_name
		return str(self.first_name) + ' ' + str(self.last_name)
	
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
	def gender(self):
		return dict(self.SEX)[self.sex]

	@property
	def table_header(self):
		return 'name,sex,born,died,birth_place,death_place'.split(',')

	@property
	def table(self):
		return [self.name,self.age,sex,born,died,birthplace,deathplace]

	@property
	def latlng(self):
		gps = []
		for fn in 'birth_place,death_place'.split(','):
			locations = field2locations(self,fn)
			if locations:
				gps.extend([location.gps for location in locations])
		if gps: return gps
		else: return None

	@property
	def latlng_roles(self):
		return ['birth_place','death_place']


	@property
	def pop_up(self):
		return pop_up(self)

	@property
	def instance_name(self):
		return self.name

	
class Movement(models.Model, info):
	'''A movement (e.g. literary) a collection of persons.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	name = models.CharField(max_length=200, null=True, blank=True)
	movement_type = models.ForeignKey(MovementType,**dargs)
	location= models.ForeignKey(Location,**dargs)
	founded = models.PositiveIntegerField(null=True,blank=True) 
	closure = models.PositiveIntegerField(null=True,blank=True) 
	notes = models.TextField(null=True,blank=True) # many to many
	description = models.TextField(blank=True)
	complete = models.BooleanField(default=False)
	approved = models.BooleanField(default=False)

	def __str__(self):
		return self.name

	@property
	def location_str(self):
		return self.location

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
		return self.name





# --- relational models ---

class PersonPersonRelation(RelationModel, info):
	'''Relation between persons. Assumed to be symmetrical.'''
	person1 = models.ForeignKey(Person, on_delete=models.CASCADE,related_name='person1')
	person2 = models.ForeignKey(Person, on_delete=models.CASCADE,related_name='person2')
	relation_type = models.ForeignKey(PersonPersonRelationType, on_delete=models.CASCADE)
	model_fields = ['person1','person2']

	class Meta:
		constraints = [models.UniqueConstraint(
			fields='person1,person2,relation_type'.split(','), 
			name = 'unique_personpersonrelation')]


class PersonLocationRelation(RelationModel,info):
	'''relation between person and location.'''
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	location = models.ForeignKey(Location, on_delete=models.CASCADE,default=None,null=True)
	relation = models.ForeignKey(PersonLocationRelationType, null=True, on_delete=models.SET_NULL)
	start_year = models.PositiveIntegerField(null=True,blank=True)
	end_year = models.PositiveIntegerField(null=True,blank=True)
	location_name = models.CharField(max_length=200, default='',null=True)
	person_name = models.CharField(max_length=200, default='',null=True)
	description= models.TextField(null=True,blank=True)
	location_field = 'location'
	model_fields = ['person','location']

	@property
	def relationship(self):
		return self.relation.name

	@property
	def relation_name(self):
		return self.relation.name

	def __str__(self):
		r = self.relation.name
		return ', '.join([self.person.name, self.location.name, r])

	@classmethod
	def create(cls):
		if hasattr(cls,'location'):
			cls.location_name = cls.location.name
		if hasattr(cls,'person'):
			cls.person_name = cls.person.first_name + ' ' + cls.person.last_name

	@property
	def primary(self):
		return self.person

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
		return self.__str__()


class PublisherManager(models.Model): #or broker
	'''Person that manages writers.'''
	# Publisher= apps.get_model('catalogue','Publisher')
	publisher = models.ForeignKey('catalogue.Publisher', 
		on_delete=models.CASCADE, related_name='publisher')
	manager = models.ForeignKey(Person, on_delete=models.CASCADE,
		related_name='manager')


class PersonTextRelation(RelationModel, info):
	'''Relation between a person and a text.'''
	role = models.ForeignKey(PersonTextRelationRole, on_delete=models.CASCADE)
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	text = models.ForeignKey('catalogue.Text', null=True, blank=True, 
		on_delete=models.CASCADE)
	published_under = models.CharField(max_length = 100,null=True,blank=True)
	model_fields = ['person','text']
	
	def __str__(self):
		m = self.person.__str__() + ' | ' + self.role.__str__() 
		m += ' | ' + self.text.__str__()
		return m

	@property
	def relationship(self):
		return self.role.name

	class Meta:
		unique_together = ['role','person','text']

	@property
	def primary(self):
		return self.person


class PersonIllustrationRelation(RelationModel, info):
	'''Relation between a person and an illustration.'''
	role = models.ForeignKey(PersonIllustrationRelationRole, 
		on_delete=models.CASCADE)
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	illustration= models.ForeignKey('catalogue.Illustration', null=True, 
		blank=True, on_delete=models.CASCADE)
	model_fields=['person','illustration']
	
	def __str__(self):
		m = self.person.__str__() + ' | ' + self.role.__str__() 
		m += ' | ' + self.illustration.__str__()
		return m

	class Meta:
		unique_together = ['role','person','illustration']

	@property
	def primary(self):
		return self.person


class PersonMovementRelation(RelationModel, info):
	'''Relation between a movement and a person.'''
	movement = models.ForeignKey(Movement, on_delete=models.CASCADE)
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	role = models.ForeignKey(PersonMovementRelationRole, on_delete=models.CASCADE)
	model_fields = ['movement','person']

	def __str__(self):
		m = self.person.__str__() + ' | ' + self.role.__str__() +' | of movement: '
		m += self.movement.__str__() 
		return m

	@property
	def primary(self):
		return self.person


class PersonPeriodicalRelation(RelationModel, info):
	'''Relation between a periodical and a person.'''
	periodical = models.ForeignKey('catalogue.Periodical', on_delete=models.CASCADE)
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	role = models.ForeignKey(PersonPeriodicalRelationRole, on_delete=models.CASCADE)
	model_fields = ['periodical','person']

	def __str__(self):
		m = self.person.__str__() + ' | ' + self.role.__str__() +' | of periodical: '
		m += self.periodical.__str__() 
		return m

	@property
	def primary(self):
		return self.person

	
	
