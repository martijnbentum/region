from django.db import models
from utils.model_util import info, id_generator


class LocType(models.Model):
	name = models.CharField(max_length = 100, unique = True)
	notes = models.TextField(default='', blank=True)


class UserLoc(models.Model, info):
	'''User defined location linked to zero or more geoloc.'''
	name = models.CharField(max_length=200) 
	loc_type = models.ForeignKey(LocType, on_delete=models.CASCADE)

	EXACT = 'E'
	APPROXIMATE = 'A'
	ROUGH = 'R'
	LOC_PRECISION = [(EXACT,'exact'),(APPROXIMATE,'approximate'),(ROUGH,'rough')]
	loc_precision=models.CharField(max_length=1,choices=LOC_PRECISION,default='A')

	FICTION = 'F'
	NON_FICTION = 'NF'
	STATUS = [(FICTION,'fiction'), (NON_FICTION,'non-fiction')]
	status = models.CharField(max_length=2,choices=STATUS,default = 'NF')

	notes = models.TextField(default='', blank=True)


class GeoLocsRelation(models.Model, info):
	'''defines a hierarchy of locations, e.g. a city is in a province.'''
	container = models.ForeignKey('GeoLoc', related_name='container',
									on_delete=models.CASCADE, default=None)
	contained = models.ForeignKey('GeoLoc', related_name='contained',
									on_delete=models.CASCADE, default=None)

	def __str__(self):
		return self.contained.name + ' is located in: ' + self.container.name

	class Meta:
		unique_together = ('container','contained')

class GeoLoc(models.Model, info):
	'''Geographic location of a specific type (e.g. city or country)'''
	name = models.CharField(max_length=200)
	CITY = 'CIT'
	COUNTRY = 'COU'
	CONTINENT = 'CON'
	REGION = 'REG'
	LOCATION_TYPE = [
		(CITY,'city'),
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
		through='GeoLocsRelation',symmetrical=False, default=None)
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
	user_locs = models.ManyToManyField(UserLoc)
	# country = CountryField()

	def __str__(self):
		return self.name 

	@property
	def attribute_names(self):
		names = 'name,location_type,geonameid,coordinates_polygon'
		names += ',latitude,longitude,notes'
		return names.split(',')

	@property
	def listify(self,attr_names=[]):
		if attr_names == []:
			names = 'name,location_type'.split(',')
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

	@property
	def contained_by_country(self):
		if self.location_type == 'COU' or self.location_type == 'CON':
			return ''
		output = []
		for location in self.contained.all():
			container= location.container
			if container.location_type == 'COU': output.append(container.name)
		return ','.join(output)

	@property
	def contained_by_region(self):
		output = []
		for location in self.contained.all():
			container= location.container
			if container.location_type == 'REG': output.append(container.name)
		return ','.join(output)

	def table_header(self):
		return 'name,type,region,country'.split(',')

	def table(self):
		o = self.listify
		o.extend([self.contained_by_region,self.contained_by_country])
		return o

		
	
	class Meta:
		ordering = ['name']




