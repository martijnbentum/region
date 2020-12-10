from django.db import models
from django.utils import timezone
import json
from locations.models import Location
from utilities.models import Language, RelationModel, instance2names
from utils.model_util import id_generator, info
from utils.map_util import field2locations, pop_up, get_location_name
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
	gps = models.CharField(max_length=300,default ='')
	gps_names = models.CharField(max_length=4000,default='')
	

	def save(self,*args,**kwargs):
		super(Person,self).save(*args,**kwargs)
		old_gps = self.gps
		self._set_gps()
		if self.gps != old_gps:super(Person,self).save()
		super(Person,self).save(*args,**kwargs)

	def _set_gps(self):
		'''sets the gps coordinates and name of related location to speed up map visualization.'''
		locations = field2locations(self,self.location_field)
		if locations:
			gps = ' - '.join([location.gps for location in locations])
			names= ' - '.join([location.name for location in locations])
			self.gps = gps
			self.gps_names = names
		else: self.gps, self.gps_names = '',''

	class Meta:
		unique_together = 'first_name,last_name,birth_year'.split(',')

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
	def location_status(self):
		locs, names = self.locations
		o = dict([[str(i),n] for i,n in zip(range(1,len(names)+1),names)])
		# return ','.join(names)
		return json.dumps(o)

	@property
	def gender(self):
		return dict(self.SEX)[self.sex]


	@property
	def latlng(self):
		try: return [eval(el) for el in self.gps.split(' - ')]
		except: return None

	@property
	def latlng_names(self):
		try: return self.gps_names.split(' - ')
		except: return None


	def pop_up(self,latlng=None):
		p = pop_up(self, latlng)
		p += '<small>' + self.gps2placetype(latlng) + '</small>'
		return p

	@property
	def instance_name(self):
		return self.name

	@property
	def plot(self):
		app_name, model_name = instance2names(self) 
		gps = str(self.gps.split(' | ')).replace("'",'')
		d = {'app_name':app_name, 'model_name':model_name, 
			'gps':gps, 'pk':self.pk}
		if d['gps'] == '[]': self._set_secondary_place(d)
		return d

	def _set_secondary_place(self,d):
		ptd = self.make_placetype_dict()
		for key in ptd:
			if 'residence' == key: 
				d['gps'] = '[' + ptd[key] + ']'
				break
			d['gps'] = '[' + ptd[key] + ']'
		

	def gps2placetype(self,latlng):
		try:
			ptd = self.make_placetype_dict()
			for key in ptd:
				if 'location_name' in key: continue
				if eval(ptd[key]) == latlng: return key.replace('_',' ')
			self.view()
		except:pass
		return '---'

	def gps2name(self,latlng):
		ln = get_location_name(self,latlng)
		if ln != '': return ln
		try:
			ptd = self.make_placetype_dict()
			for key in ptd:
				if eval(ptd[key]) ==latlng: return ptd[key+'_location_name']
		except:pass
		return '-'
		
	def make_placetype_dict(self):
		d = {}
		for name in  'birth_place,death_place'.split(','):
			if hasattr(self,name):
				try: 
					d[name] = getattr(self,name).gps 
					d[name+'_location_name'] = getattr(self,name).name
				except:continue
		for plr in self.personlocationrelation_set.all():
			if None in [getattr(plr,n) for n in 'location,person,relation'.split(',')]:continue
			d[plr.relation.name] =  plr.location.gps 
			d[plr.relation.name+'_location_name'] = plr.location.name
		return d


	
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
	gps = models.CharField(max_length=300,default ='')
	gps_names = models.CharField(max_length=4000,default='')
	location_field = 'location'


	def save(self,*args,**kwargs):
		super(Movement,self).save(*args,**kwargs)
		old_gps = self.gps
		self._set_gps()
		if self.gps != old_gps:super(Movement,self).save()
		super(Movement,self).save(*args,**kwargs)

	def _set_gps(self):
		'''sets the gps coordinates and name of related location to speed up map visualization.'''
		locations = field2locations(self,self.location_field)
		if locations:
			gps = ' | '.join([location.gps for location in locations])
			names= ' | '.join([location.name for location in locations])
			self.gps = gps
			self.gps_names = names
		else: self.gps, self.gps_names = '',''

	class Meta:
		unique_together = 'name,founded'.split(',')

	def __str__(self):
		return self.name

	@property
	def location_str(self):
		return self.location_string

	@property
	def latlng(self):
		try: return [eval(el) for el in self.gps.split(' - ')]
		except: return None

	@property
	def latlng_names(self):
		try: return self.gps_names.split(' || ')
		except: return None

	@property
	def location_string(self):
		try:return ', '.join(self.latlng_names)
		except: return ''


	def pop_up(self,latlng = None):
		return pop_up(self)	

	@property
	def instance_name(self):
		return self.name

	@property
	def plot(self):
		app_name, model_name = instance2names(self) 
		gps = str(self.gps.split(' | ')).replace("'",'')
		d = {'app_name':app_name, 'model_name':model_name, 
			'gps':gps, 'pk':self.pk}
		return d

	def gps2name(self,latlng):
		return get_location_name(self,latlng)



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
		try:
			r = self.relation.name
			return ', '.join([self.person.name, self.location.name, r])
		except:
			self.view()
			return 'could not generate str representation'

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

	def pop_up(self,latlng =None):
		return pop_up(self,latlng)	

	@property
	def instance_name(self):
		return self.__str__()

	@property
	def plot(self):
		pd = self.person.plot
		pd['gps'] = self.location.gps
		return pd


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

	
	
