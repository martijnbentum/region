from django.db import models
from django.utils import timezone
import json
from locations.models import Location
from utilities.models import Language, RelationModel,GroupTag 
from utils.model_util import id_generator, info,instance2names
from utils.map_util import field2locations, pop_up, get_location_name,gps2latlng
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
	group_tags= models.ManyToManyField(GroupTag,blank=True, default= None)
	

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
			gps = ' | '.join([location.gps for location in locations if location.gps])
			names= ' | '.join([location.name for location in locations if location.gps])
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

	@property
	def instance_name(self):
		return self.name
	
	def __str__(self):
		return self.name

	@property
	def born(self):
		return self.birth_year

	@property
	def died(self):
		return self.death_year

	@property
	def life(self):
		m =''
		if self.born:m += 'born ' + str(self.birth_year) 
		if self.born and self.died: m += ', '
		if self.died:m += 'died ' + str(self.death_year)
		if self.born and self.died: m += ' (age ' + str(self.death_year -self.birth_year) + ')'
		return m

	@property
	def gender(self):
		return dict(self.SEX)[self.sex]

	@property
	def latlng(self):
		return gps2latlng(self.gps)

	@property
	def latlng_names(self):
		try: return self.gps_names.split(' - ')
		except: return None

	@property
	def pseudonyms(self):
		return ' | '.join([x.name for x in self.pseudonym.all()])
		
	def pop_up(self,latlng=None):
		m = ''
		if self.life: m += '<p><small>' + self.life + '</small></p>'
		pseudonyms = self.pseudonyms
		if pseudonyms: m += '<p><small>pseudonym <b>' + pseudonyms + '</b></small></p>'
		p = pop_up(self, latlng, extra_information = m)
		return p

	def plot(self):
		app_name, model_name = instance2names(self) 
		gps = str(self.gps.split(' | ')).replace("'",'')
		d = {'app_name':app_name, 'model_name':model_name, 
			'gps':gps, 'pk':self.pk}
		if d['gps'] == '[]': self._set_secondary_place(d)
		return d

	def _set_secondary_place(self,d):
		ptd = self.make_placetype_dict()
		for relation_name in ptd:
			if 'residence' == relation_name: 
				d['gps'] = '[' + ptd[relation_name][0] + ']'
				break
			d['gps'] = '[' + ptd[relation_name][0] + ']'
		

	def latlng2placetype(self,latlng):
		'''return the relation between the place and the person, e.g. residence.'''
		try:
			ptd = self.make_placetype_dict()
			for relation_name in ptd:
				if 'location_name' in relation_name: continue
				for gps in ptd[relation_name]:
					if eval(gps) == latlng: return relation_name.replace('_',' ')
			self.view()
		except:pass
		return ''

	def latlng2name(self,latlng):
		'''returns the location name based on on the latlng input
		uses index of gps corresponding with latlng and gps_names to return correct name
		'''
		ln = get_location_name(self,latlng)
		if ln == '':
			try:
				ptd = self.make_placetype_dict()
				for relation_name in ptd:
					if 'location_name' in relation_name: continue
					for i,gps in enumerate(ptd[relation_name]):
						if eval(gps) ==latlng: ln = ptd[relation_name+'_location_name'][i]
			except:pass
		pt = self.latlng2placetype(latlng)
		if ln and pt: return '<b>'+ln + '</b>, ' + pt
		if ln: return ln
		return pt
		
	def make_placetype_dict(self):
		'''creates a dictionary that maps the relation name between the person and location
		to the gps string saved on the person instance
		[relation name] + '_location_name' gives the corresponding location name
		'''
		d = {}
		for name in  'birth_place,death_place'.split(','):
			if hasattr(self,name):
				try: 
					d[name] = [getattr(self,name).gps]
					d[name+'_location_name'] = [getattr(self,name).name]
				except:continue
		for plr in self.personlocationrelation_set.all():
			if None in [getattr(plr,n) for n in 'location,person,relation'.split(',')]:continue
			if plr.relation.name not in d.keys():
				d[plr.relation.name], d[plr.relation.name +'_location_name'] = [], []
			d[plr.relation.name].append( plr.location.gps )
			d[plr.relation.name+'_location_name'].append( plr.location.name )
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
			gps = ' | '.join([location.gps for location in locations if location.gps])
			names= ' | '.join([location.name for location in locations if location.gps])
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
		return gps2latlng(self.gps)

	@property
	def latlng_names(self):
		try: return self.gps_names.split(' || ')
		except: return None

	@property
	def location_string(self):
		try:return ', '.join(self.latlng_names)
		except: return ''

	def pop_up(self,latlng):
		m = ''
		if self.movement_type: 
			m += '<p><small><b>' + self.movement_type.name + '</b> movement</small></p>'
		if self.founded: m += '<p><small>founded <b>' + str(self.founded)
		if self.founded and self.closure: m += '</b>, '
		else: m += '</b></small></p>'
		if not m and self.founded: m += '<p><small>'
		if self.closure: m += 'closure <b>' + str(self.closure) + '</b></small></p>'
		return pop_up(self,latlng,extra_information=m)


	@property
	def instance_name(self):
		return self.name

	def plot(self):
		app_name, model_name = instance2names(self) 
		gps = str(self.gps.split(' | ')).replace("'",'')
		d = {'app_name':app_name, 'model_name':model_name, 
			'gps':gps, 'pk':self.pk}
		return d

	def latlng2name(self,latlng):
		return get_location_name(self,latlng)



# --- relational models ---

class PersonPersonRelation(RelationModel, info):
	'''Relation between persons. Assumed to be symmetrical.'''
	person1 = models.ForeignKey(Person, on_delete=models.CASCADE,related_name='person1')
	person2 = models.ForeignKey(Person, on_delete=models.CASCADE,related_name='person2')
	relation_type = models.ForeignKey(PersonPersonRelationType, on_delete=models.CASCADE)
	model_fields = ['person1','person2']
	relation_field = 'relation_type'

	class Meta:
		constraints = [models.UniqueConstraint(
			fields='person1,person2,relation_type'.split(','), 
			name = 'unique_personpersonrelation')]


	@property
	def relation_name(self):
		return self.relation.name

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
	relation_field = 'relation'

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


	def pop_up(self,main_instance=None, latlng =None):
		m = self.person.pop_up(self.location.latlng)	
		return m

	@property
	def instance_name(self):
		return self.__str__()

	def plot(self):
		d = super().plot()
		d['layer_name'] = 'Person'
		return d

	'''
	def plot(self):
		app_name, model_name = instance2names(self) 
		pan, pmn= instance2names(self.person) 
		gps = str(self.location.gps.split(' | ')).replace("'",'')
		d = {'app_name':app_name, 'model_name':model_name, 
			'gps':gps, 'pk':self.pk,'layer_name':pmn}
		return d
	'''


class PublisherManager(models.Model): #or broker
	'''Person that manages writers.'''
	# Publisher= apps.get_model('catalogue','Publisher')
	publisher = models.ForeignKey('catalogue.Publisher', 
		on_delete=models.CASCADE, related_name='publisher')
	manager = models.ForeignKey(Person, on_delete=models.CASCADE,
		related_name='manager')
	model_fields = ['person','location']

	@property
	def relation_name(self):
		return 'Manager'

class PersonTextRelation(RelationModel, info):
	'''Relation between a person and a text.'''
	role = models.ForeignKey(PersonTextRelationRole, on_delete=models.CASCADE)
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	text = models.ForeignKey('catalogue.Text', null=True, blank=True, 
		on_delete=models.CASCADE)
	published_under = models.CharField(max_length = 100,null=True,blank=True)
	model_fields = ['person','text']
	relation_field = 'role'
	
	def __str__(self):
		m = self.person.__str__() + ' | ' + self.role.__str__() 
		m += ' | ' + self.text.__str__()
		return m

	@property
	def relation_name(self):
		return self.role.name

	class Meta:
		unique_together = ['role','person','text']

	@property
	def primary(self):
		return self.person

	def pop_up(self,main_instance):
		m = super().pop_up(main_instance)
		m += '<small>'+self.person.name + ' is the <b>' +self.relation_name + '</b></small>'
		return m

	'''
	def pop_up(self,main_instance,latlng = None):
		self.set_other(main_instance)
		if not self.other: return 'could not construct relation'
		latlng = gps2latlng(self.other.gps)
		m = self.other.pop_up(latlng)
		m += '<small>'+self.person.name + ' is the <b>' +self.relation_name + '</b></small>'
		return m

	def set_other(self,main_instance):
		if main_instance == self.person: self.other = self.text
		elif main_instance == self.text: self.other = self.person
		else: self.other = False
		
	def plot(self):
		app_name, model_name = instance2names(self) 
		oan,omn = instance2names(self.other)
		gps = str(self.other.gps.split(' | ')).replace("'",'')
		d = {'app_name':app_name, 'model_name':model_name, 
			'gps':gps, 'pk':self.pk,'layer_name':omn}
		return d
	'''



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
	relation_field = 'role'

	def __str__(self):
		m = self.person.__str__() + ' | ' + self.role.__str__() +' | of movement: '
		m += self.movement.__str__() 
		return m

	@property
	def relation_name(self):
		return self.role.name

	@property
	def primary(self):
		return self.person

	def pop_up(self,main_instance):
		m = super().pop_up(main_instance)
		m += '<small>Role: <b>'+self.relation_name + '</b></small>'
		return m

	'''
	def pop_up(self,main_instance,latlng = None):
		self.set_other(main_instance)
		if not self.other: return 'could not construct relation'
		latlng = gps2latlng(self.other.gps)
		m = self.other.pop_up(latlng)
		m += '<small>Role: <b>'+self.relation_name + '</b></small>'
		return m

	def set_other(self,main_instance):
		if main_instance == self.person: self.other = self.movement
		elif main_instance == self.movement: self.other = self.person
		else: self.other = False

	def plot(self):
		app_name, model_name = instance2names(self) 
		oan,omn = instance2names(self.other)
		gps = str(self.other.gps.split(' | ')).replace("'",'')
		d = {'app_name':app_name, 'model_name':model_name, 
			'gps':gps, 'pk':self.pk,'layer_name':omn}
		return d
	'''

class PersonPeriodicalRelation(RelationModel, info):
	'''Relation between a periodical and a person.'''
	periodical = models.ForeignKey('catalogue.Periodical', on_delete=models.CASCADE)
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	role = models.ForeignKey(PersonPeriodicalRelationRole, on_delete=models.CASCADE)
	model_fields = ['periodical','person']
	relation_field = 'role'

	def __str__(self):
		m = self.person.__str__() + ' | ' + self.role.__str__() +' | of periodical: '
		m += self.periodical.__str__() 
		return m

	@property
	def relation_name(self):
		return self.role.name

	@property
	def primary(self):
		return self.person

	def pop_up(self,main_instance):
		m = super().pop_up(main_instance)
		m += '<small>Role: '+self.role.name + '</small>'
		return m

	'''
	def pop_up(self,main_instance,latlng = None):
		self.set_other(main_instance)
		if not self.other: return 'could not construct relation'
		latln = gps2latlng(self.other.gps)
		m = self.other.pop_up(latlng)
		m += '<small>Role: '+self.role.name + '</small>'
		return m

	def set_other(self,main_instance):
		if main_instance == self.person: self.other = self.periodical
		elif main_instance == self.periodical: self.other = self.person
		else: self.other = False
	
	def plot(self):
		app_name, model_name = instance2names(self) 
		oan,omn = instance2names(self.other)
		gps = str(self.other.gps.split(' | ')).replace("'",'')
		d = {'app_name':app_name, 'model_name':model_name, 
			'gps':gps, 'pk':self.pk,'layer_name':omn}
		return d
	'''
