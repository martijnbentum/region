from django.db import models
from colorfield.fields import ColorField
from utils.model_util import info, id_generator
from utils.general import flatten_lol
from utilities.models import SimpleModel
from partial_date import PartialDateField


def make_simple_model(name):
	exec('class '+name + '(SimpleModel):\n\tpass',globals())

names = 'LocationType,LocationStatus,LocationPrecision'
names = names.split(',')

for name in names:
	make_simple_model(name)


class LocationRelation(models.Model, info):
	'''defines a hierarchy of locations, e.g. a city is in a province.'''
	container = models.ForeignKey('Location', related_name='container',
									on_delete=models.CASCADE, default=None)
	contained = models.ForeignKey('Location', related_name='contained',
									on_delete=models.CASCADE, default=None)

	def __str__(self):
		'''deleting a Location can resultin an error due to the easy audit app.
		it needed the string representation of this model, while the Location instance
		did not exist anymore '''
		try:return self.contained.name + ' is located in: ' + self.container.name
		except:return ''

	class Meta:
		unique_together = ('container','contained')


class Location(models.Model, info):
	'''Geographic location of a specific type (e.g. city or country)'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	gpsargs = {'blank':True,'null':True,'max_digits':8,'decimal_places':5}
	name = models.CharField(max_length=200)
	location_type= models.ForeignKey(LocationType,**dargs)
	location_status = models.ForeignKey(LocationStatus,**dargs)
	location_precision = models.ForeignKey(LocationPrecision,**dargs)
	relations = models.ManyToManyField('self',
		through='LocationRelation',symmetrical=False, default=None)
	geonameid = models.CharField(max_length=12,default= '',unique = True)
	coordinates_polygon = models.CharField(max_length=3000, blank=True ,null=True)
	latitude=models.DecimalField(**gpsargs)
	longitude=models.DecimalField(**gpsargs)
	information = models.TextField(default='',blank=True)
	active = models.BooleanField(default=False)
	notes = models.TextField(default='',blank=True)

	class Meta:
		ordering = ['name']
		unique_together = 'name,latitude,longitude'.split(',')

	def save(self):
		if not self.pk and not self.geonameid:
			try: geonameid = eval(self.information)['geonameid']
			except: 
				geonameid = id_generator(length = 27)
				self.active = True
			self.geonameid = geonameid
		super(Location, self).save()

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
		if self.location_type.name == 'country' or self.location_type.name == 'continent':
			return ''
		output = []
		for location in self.contained.all():
			container= location.container
			if container.location_type.name == 'country': output.append(container.name)
		return ','.join(list(set(output)))

	@property
	def contained_by_region(self):
		output = []
		for location in self.contained.all():
			container= location.container
			if container.location_type.name == 'region': output.append(container.name)
		return ','.join(output)


	@property
	def country(self):
		country = self.contained_by_country
		if country == '':
			try: country = eval(self.information)['country']
			except: pass
			if country == 'NA':country = ''
		return country

	@property
	def region(self):
		region = self.contained_by_region
		if region == '':
			if self.country == '':return ''
			try: region = eval(self.information)['admin1_name']
			except: region = ''
			if region == 'NA': region = ''
		return region

	@property
	def gps(self):
		try: return str(round(self.latitude,2)) + ', ' + str(round(self.longitude,2))
		except: return ''

	@property
	def latlng(self):
		return self.gps

	def table_header(self):
		return 'name,type,region,country'.split(',')

	def table(self):
		o = self.listify
		o.extend([self.contained_by_region,self.contained_by_country])
		return o


class Style(models.Model, info):
	name = models.CharField(max_length=200)
	color = ColorField(default='#FF0000')
	stroke_opacity = models.FloatField(default = 0.8,)
	stroke_weight = models.IntegerField(default = 2)
	fill_opacity = models.FloatField(default = 0.3)
	dashed = models.BooleanField(default =False)
	z_index = models.IntegerField(default = 0)
	

	def __str__(self):
		return self.name + ' ' + self.color

class Figure(models.Model, info):
	'''figure to be plotted on a map.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	name = models.CharField(max_length=200)
	description= models.TextField(default='',blank=True)
	style= models.ForeignKey(Style,**dargs)
	start_date = PartialDateField(null=True,blank=True)
	end_date = PartialDateField(null=True,blank=True)
	geojson = models.FileField(upload_to='geojson/',null=True,blank=True) # ?
	district_number=models.IntegerField(blank=True,null=True)
	city = models.CharField(max_length=200)


# --------------------------------------------------

