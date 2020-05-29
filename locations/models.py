from django.db import models
from utils.model_util import info, id_generator
from utils.general import flatten_lol


class LocType(models.Model, info):
	name = models.CharField(max_length = 100, unique = True)
	notes = models.TextField(default='', blank=True)

	def __str__(self):
		return self.name 


class UserLoc(models.Model, info):
	'''User defined location linked to zero or more geoloc.'''
	name = models.CharField(max_length=200) 
	loc_type = models.ForeignKey(LocType, on_delete=models.CASCADE)
	EXACT = 'exact'
	APPROXIMATE = 'approximate'
	ROUGH = 'rough'
	LOC_PRECISION = [(EXACT,'exact'),(APPROXIMATE,'approximate'),(ROUGH,'rough')]
	loc_precision=models.CharField(max_length=15,choices=LOC_PRECISION,default='A')

	FICTION = 'fiction'
	NON_FICTION = 'non-fiction'
	STATUS = [(FICTION,'fiction'), (NON_FICTION,'non-fiction')]
	status = models.CharField(max_length=15,choices=STATUS,default = 'NF')
	notes = models.TextField(default='', blank=True)

	def __str__(self):
		return self.name 

	@property
	def latitudes(self):
		return [gl.latitude for gl in self.geoloc_set.all()]

	@property
	def longitudes(self):
		return [gl.longitude for gl in self.geoloc_set.all()]

	@property
	def latitude(self):
		return self.latitudes[0]

	@property
	def longitude(self):
		return self.longitudes[0]
	
	@property
	def multiple_geolocs(self):
		return len(self.geoloc_set.all()) > 1

	@property
	def n_geolocs(self):
		return len(self.geoloc_set.all()) 

	@property
	def country(self):
		gl = self.geoloc_set.all()
		# if len(gl) == 0: return ''
		gr = flatten_lol([GeoLocsRelation.objects.filter(contained__geonameid= x.geonameid) 
			for x in gl])
		countries = list(set(
			[x.container.name for x in gr if x.container.location_type == 'COUNTRY']))
		return ','.join(countries)

	@property
	def region(self):
		if self.country == '':return ''
		regions = []
		for gl in self.geoloc_set.all():
			try: regions.append( eval(gl.information)['admin1_name'] )
			except: pass
		regions = list(set(regions))
		if 'NA' in regions: regions.remove('NA')
		return ','.join(regions)

	@property
	def gps(self):
		gps = [gl.gps for gl in self.geoloc_set.all()]
		if gps: return '; '.join(gps)
		else: return '' 

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
	CITY = 'CITY'
	COUNTRY = 'COUNTRY'
	CONTINENT = 'CONTINENT'
	REGION = 'REGION'
	LOCATION_TYPE = [
		(CITY,'city'),
		(COUNTRY,'country'),
		(CONTINENT,'continent'),
		(REGION,'region'),
	]
	location_type= models.CharField(
		max_length=9,
		choices=LOCATION_TYPE,
		default = CITY
	)
	relations = models.ManyToManyField('self',
		through='GeoLocsRelation',symmetrical=False, default=None)
	geonameid = models.CharField(
		max_length=12, 
		default= '',
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
	information = models.TextField(default='',blank=True)
	notes = models.TextField(default='',blank=True)
	user_locs = models.ManyToManyField(UserLoc)
	# country = CountryField()

	def save(self):
		if not self.pk:
			try: geonameid = eval(self.info)['geonameid']
			except: geonameid = id_generator(length = 27)
			self.geonameid = geonameid
		super(GeoLoc, self).save()

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
		if self.location_type == 'COUNTRY' or self.location_type == 'CONTINENT':
			return ''
		output = []
		for location in self.contained.all():
			container= location.container
			if container.location_type == 'COUNTRY': output.append(container.name)
		return ','.join(list(set(output)))

	@property
	def contained_by_region(self):
		output = []
		for location in self.contained.all():
			container= location.container
			if container.location_type == 'REGION': output.append(container.name)
		return ','.join(output)


	@property
	def country(self):
		return self.contained_by_country

	@property
	def region(self):
		if self.country == '':return ''
		try: region = eval(self.information)['admin1_name']
		except: region = ''
		if region == 'NA': region = ''
		return region

	@property
	def gps(self):
		return str(round(self.latitude,2)) + ', ' + str(round(self.longitude,2))

	def table_header(self):
		return 'name,type,region,country'.split(',')

	def table(self):
		o = self.listify
		o.extend([self.contained_by_region,self.contained_by_country])
		return o

		
		
	
	class Meta:
		ordering = ['name']




