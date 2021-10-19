from django.db import models
from django.conf import settings
from django.utils import timezone
import glob
from locations.models import Location
from utilities.models import Language, RelationModel, SimpleModel, GroupTag
from utils.model_util import id_generator, info,instance2names, get_empty_fields
from utils.map_util import field2locations, pop_up, get_location_name,gps2latlng
import os
from partial_date import PartialDateField
import time

def make_simple_model(name):
	'''creates a new model based on name, uses the abstract class SimpleModel.
	'''
	exec('class '+name + '(SimpleModel,info):\n\tpass',globals())

names = 'CopyRight,Genre,TextType,TextTextRelationType,Audience'
names += ',PublicationType,IllustrationCategory'
names += ',IllustrationIllustrationRelationType,IllustrationType'
names = names.split(',')

for name in names:
	make_simple_model(name)
			

class Item(models.Model):
	'''abstract model for non simple/ non relational catalogue models.
	sets fields that are used by most models and defines methods used by 
	most models
	'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	description = models.TextField(blank=True)
	notes = models.TextField(default='',blank=True, null=True)
	complete = models.BooleanField(default=False)
	approved = models.BooleanField(default=False)
	incomplete = models.BooleanField(default=False)
	source_link= models.CharField(max_length=1000,blank=True,null=True)
	copyright = models.ForeignKey(CopyRight,**dargs)
	gps = models.CharField(max_length=300,default ='')
	gps_names = models.CharField(max_length=4000,default='')
	loc_ids = models.CharField(max_length=300,default ='')
	group_tags= models.ManyToManyField(GroupTag,blank=True, default= None)
	location_field = 'location'
	
	def __str__(self):
		return self.instance_name

	def save(self,*args,**kwargs):
		'''sets the gps coordinates and names field after saving based 
		on the fk location
		'''
		super(Item,self).save(*args,**kwargs)
		old_gps = self.gps
		self._set_gps()
		if self.gps != old_gps:super(Item,self).save()
		super(Item,self).save(*args,**kwargs)

	def _set_gps(self):
		'''sets the gps coordinates and name of related location to speed 
		up map visualization.
		'''
		locations = field2locations(self,self.location_field)
		if locations:
			gps = ' | '.join([l.gps for l in locations if l.gps])
			names= ' | '.join([l.name for l in locations if l.gps])
			ids = ','.join([str(l.pk) for l in locations])
			self.gps = gps
			self.gps_names = names
			self.loc_ids = ids
		else: self.gps, self.gps_names, self.loc_ids = '','',''

	def empty_fields(self,fields = []):
		return get_empty_fields(self,fields, default_is_empty = True)

	@property
	def latlng(self):
		return gps2latlng(self.gps)

	@property
	def latlng_names(self):
		try: return self.gps_names.split(' - ')
		except: return None

	@property
	def location_string(self):
		try:return ', '.join(self.latlng_names)
		except: return ''

	def pop_up(self, latlng=None):
		'''creates html for the pop up for map visualization.'''
		return pop_up(self,latlng)	

	@property
	def instance_name(self):
		if hasattr(self,'title'):
			return self.title
		if hasattr(self,'name'):
			return self.name
		if hasattr(self,'caption'):
			return self.caption
		else: 
			m = 'please override instance_name property with '
			m += 'correct "name" field'
			raise ValueError(m)

	def plot(self):
		'''provides information to plot an instance on the map'''
		app_name, model_name = instance2names(self) 
		gps = str(self.gps.split(' | ')).replace("'",'')
		d = {'app_name':app_name, 'model_name':model_name, 
			'gps':gps, 'pk':self.pk}
		return d

	def latlng2name(self,latlng):
		return get_location_name(self,latlng)

	@property
	def identifier(self):
		i = self._meta.app_label + '_' + self._meta.model_name 
		i += '_' + str( self.pk )
		return i

	class Meta:
		abstract = True



# --- non simple / non relational catalogue models ---

class Text(Item, info):
	'''a text can be an entire book or article or a subsection thereof.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	title = models.CharField(max_length=300)
	setting = models.CharField(max_length=300,blank=True)
	language = models.ForeignKey(Language, **dargs)
	genre = models.ForeignKey(Genre, **dargs)
	text_type = models.ForeignKey(TextType, **dargs)
	# upload = models.FileField(upload_to='texts/',blank=True,null=True) # ?
	relations = models.ManyToManyField('self',
		through='TextTextRelation',symmetrical=False, default=None)
	location= models.ManyToManyField(Location,blank=True, default= None)
	person = models.CharField(max_length=2000,blank=True,null=True)

	def _set_person(self):
		names = [] 
		for ptr in self.persontextrelation_set.all():
			names.append(ptr.person.full_name)
		self.person = '; '.join(names)
		self.save()
			
	class Meta:
		unique_together = 'title,setting,language'.split(',')

	def latlng2name(self,latlng):
		location_name = super().latlng2name(latlng)
		if location_name:
			return 'Text situated in <b>' +location_name + '</b>'
		else: return '<p></p>'

	def pop_up(self,latlng):
		m = ''
		if self.language: m += '<p><small>language <b>' + self.language.name 
		if self.language and self.genre: m += '</b>, '
		else: m += '</b></small></p>'
		if not m and self.genre: m += '<p><small>'
		if self.genre: m += 'genre <b>' + self.genre.name + '</b></small></p>'
		return pop_up(self,latlng,extra_information=m)

	@property
	def get_dates(self):
		'''text object does not contain date, 
		only the linked publication has a date.
		a text can have multiple dates (if it is linked to 
		multiple publications)
		the date is the date of publication of the publication instance
		returns a list of partialdate objects
		'''
		if hasattr(self,'_dates'): return self._dates
		tpr =  self.textpublicationrelation_set.all()
		if not tpr: return ''
		o = []
		for x in tpr:
			if not hasattr(x,'publication'): continue
			date = x.publication.date
			if date: o.append(date)
		self._dates = o
		return o
			

def make_filename(instance, filename):
	'''creates a filename for uploaded images'''
	app_name, model_name = instance2names(instance)
	name,ext = os.path.splitext(filename)
	name += '_django-'+time.strftime('%y-%m-%d-%H-%M') + ext
	pn = model_name.lower() +'/'+ name
	return pn

class Illustration(Item, info):
	'''a illustration typically part of publication'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	caption =  models.CharField(max_length=300,null=True,blank=True)
	category = models.ForeignKey(IllustrationCategory,
		on_delete=models.SET_NULL,
		blank=True,null=True,related_name='Illustration')
	categories=models.ManyToManyField(IllustrationCategory,blank=True,
		related_name='Illustrations') 
	page_number = models.CharField(max_length=50, default = '', blank=True)
	upload= models.ImageField(upload_to=make_filename,null=True,blank=True)
	relations = models.ManyToManyField('self',
		through='IllustrationIllustrationRelation',symmetrical=False, 
		default=None)
	illustration_type = models.ForeignKey(IllustrationType, **dargs)
	location_field = ''
	image_filename = models.CharField(max_length=500,default='',blank=True,
		null=True)
	person = models.CharField(max_length=2000,blank=True,null=True)

	def _set_person(self):
		names = [] 
		for pir in self.personillustrationrelation_set.all():
			names.append(pir.person.full_name)
		self.person = '; '.join(names)
		self.save()

	class Meta:
		unique_together = 'caption,image_filename,page_number'.split(',')

	@property
	def get_dates(self):
		'''illustration object does not contain date, 
		only the linked publication has a date.
		a illustration can have multiple dates 
		(if it is linked to multiple publications)
		the date is the date of publication of the publication instance
		returns a list of partialdate objects
		'''
		if hasattr(self,'_dates'): return self._dates
		tpr =  self.illustrationpublicationrelation_set.all()
		if not tpr: return ''
		o = []
		for x in tpr:
			if not hasattr(x,'publication'): continue
			date = x.publication.date
			if date: o.append(date)
		self._dates = o
		return o
	

class Publisher(Item, info):
	'''Company that publishes works.'''
	name = models.CharField(max_length=300, unique=True)
	location= models.ManyToManyField(Location,blank=True,default=None)
	founded = models.PositiveIntegerField(null=True,blank=True) 
	closure = models.PositiveIntegerField(null=True,blank=True) 
	person = models.CharField(max_length=2000,blank=True,null=True)

	def _set_person(self):
		names = [] 
		for p in self.publisher.all():
			names.append(p.manager.full_name)
		self.person = '; '.join(names)
		self.save()

	class Meta:
		ordering = ['name']
		unique_together = 'name,founded'.split(',')

	@property
	def get_dates(self):
		if not self.founded: return ''
		return [self.founded]

	def pop_up(self,latlng):
		m = ''
		if self.founded: m += '<p><small>founded <b>' + str(self.founded)
		if self.founded and self.closure: m += '</b>, '
		else: m += '</b></small></p>'
		if not m and self.founded: m += '<p><small>'
		if self.closure: 
			m += 'closure <b>' + str(self.closure) + '</b></small></p>'
		return pop_up(self,latlng,extra_information=m)


class Publication(Item, info):
	'''The publication of a text or collection of texts and illustrations'''
	title = models.CharField(max_length=300,null=True)
	publisher = models.ManyToManyField(Publisher,blank=True)
	form = models.ForeignKey(PublicationType,on_delete=models.SET_NULL,
		null=True)
	issue = models.PositiveIntegerField(default=0,blank=True) 
	volume = models.PositiveIntegerField(default=0,blank=True) 
	year = models.PositiveIntegerField(null=True,blank=True) 
	# obsolete, replace by date
	date = PartialDateField(null=True,blank=True)
	location = models.ManyToManyField(Location,blank=True,default=None) 
	pdf = models.FileField(upload_to='publication/',null=True,blank=True) # ?
	cover = models.ImageField(upload_to='publication/',null=True,blank=True)
	publisher_names = models.CharField(max_length = 500, null=True,
		blank=True,default='')

	def pop_up(self,latlng):
		m = ''
		if self.publisher_names: 
			m += '<p><small>published by <b>'+self.publisher_names
			m +='</b></small></p>'
		if self.volume: m+='<p><small>volume <b>' + str(self.volume)
		if not self.issue: m+= '</b></small></p>'
		if not self.volume and self.issue:m+= '<p><small>'
		if self.issue and self.volume: m += '</b>, '
		if self.issue: m += 'issue <b>'+ str(self.issue) +'</b></small></p>'
		if self.date: 
			m+='<p><small>published in <b>'+ self.date.name+'</b></small></p>'
		return pop_up(self,latlng,extra_information=m)

	class Meta:
		unique_together=[['title','publisher_names','date','issue','volume']]


	@property
	def publisher_str(self):
		return ' | '.join([x.name for x in self.publisher.all()])
		# return self.publisher_names

	@property
	def location_str(self):
		return ' | '.join([pu.name for pu in self.location.all()])

	@property
	def get_dates(self):
		if not self.date: return ''
		return [self.date]

	@property
	def title_exact(self):
		m = self.title
		add_bracket = False
		if self.date or self.issue or self.volume: 
			m += ' ('
			add_bracket = True
		if self.volume: m += 'vol. ' +str(self.volume) 
		if (self.volume and self.issue) or (self.volume and self.date):
			m += ', '
		if self.issue: m += 'n. ' + str(self.issue)
		if self.issue and self.date:m += ', '
		if self.date: m += self.date.pretty_string() 
		if add_bracket: m +=')'
		return m


class Periodical(Item, info):
	'''Recurrent publication.'''
	title = models.CharField(max_length=300)
	founded = models.PositiveIntegerField(null=True,blank=True) 
	closure = models.PositiveIntegerField(null=True,blank=True) 
	location= models.ManyToManyField(Location,blank=True,default =None)
	person = models.CharField(max_length=2000,blank=True,null=True)

	def _set_person(self):
		names = [] 
		for ppr in self.personperiodicalrelation_set.all():
			names.append(ppr.person.full_name)
		self.person = '; '.join(names)
		self.save()

	@property
	def get_dates(self):
		if not self.founded: return ''
		return [self.founded]

	class Meta:
		unique_together = 'title,founded'.split(',')

	def pop_up(self,latlng):
		m = ''
		if self.founded: m += '<p><small>founded <b>' + str(self.founded)
		if self.founded and self.closure: m += '</b>, '
		else: m += '</b></small></p>'
		if not m and self.founded: m += '<p><small>'
		if self.closure: 
			m += 'closure <b>' + str(self.closure) + '</b></small></p>'
		x = self.periodicalpublicationrelation_set.all()
		n=' | '.join(list(set([y.publication.publisher_names for y in x])))
		names = n
		if names: 
			m += '<p><small>published by <b>' + names + '</b></small></p>'
		return pop_up(self,latlng,extra_information=m)


# ---- relation objects, e.g text publication relation etc. ----

class TextPublicationRelation(RelationModel): 
	'''Links a text with a publication.'''
	text = models.ForeignKey(Text, on_delete=models.CASCADE)
	publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
	start_page = models.CharField(max_length=5,null=True,blank=True)
	end_page = models.CharField(max_length=5,null=True,blank=True)
	model_fields = ['text','publication']

	def __str__(self):
		try:
			m =  self.text.title+ ' is a part of '
			m += self.publication.title
			return m
		except:
			print('textpublicationrelation name could not be made')
			return ''

	@property
	def primary(self):
		return self.text
		

class TextReviewPublicationRelation(RelationModel): 
	'''Links a review text with a publication.'''
	text = models.ForeignKey(Text, on_delete=models.CASCADE)
	publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
	model_fields = ['text','publication']

	def __str__(self):
		m =  self.text.title+ ' is a review of '
		m += self.publication.title
		return m

	@property
	def primary(self):
		return self.text


class IllustrationPublicationRelation(RelationModel): 
	'''Links a illustration with a publication.'''
	illustration = models.ForeignKey(Illustration, on_delete=models.CASCADE)
	publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
	page = models.CharField(max_length=5,null=True,blank=True)
	model_fields = ['illustration','publication']

	def __str__(self):
		m =  self.illustration.caption+ ' is a part of '
		m += self.publication.title
		return m

	@property
	def primary(self):
		return self.illustration


class PeriodicalPublicationRelation(RelationModel, info):
	'''linking a periodical to a publication 
	(a specific issue of a periodical).'''
	periodical= models.ForeignKey(Periodical, on_delete=models.CASCADE)
	publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
	volume= models.PositiveIntegerField(null=True,blank=True)
	issue= models.PositiveIntegerField(null=True,blank=True)
	model_fields = ['periodical','publication']

	def __str__(self):
		m =  self.periodical.title+ ' is a periodical in '
		m += self.publication.title
		return m

	@property
	def primary(self):
		return self.periodical


class TextTextRelation(models.Model, info):
	'''connects two texts with a specific type of relation e.g. original 
	and translation (primary, secondary).'''
	primary = models.ForeignKey('Text', related_name='primary',
									on_delete=models.CASCADE, default=None)
	secondary = models.ForeignKey('Text', related_name='secondary',
									on_delete=models.CASCADE, default=None)
	relation_type = models.ForeignKey(TextTextRelationType, 
									on_delete=models.CASCADE, default=None)
	model_fields = ['primary','secondary']

	def __str__(self):
		m =  self.relation_type.name +' relation between ' 
		m += self.secondary.title +' and '
		m += self.primary.title
		return m


class IllustrationIllustrationRelation(models.Model, info):
	'''connects two texts with a specific type of relation e.g. original 
	and translation (primary, secondary).'''
	primary = models.ForeignKey('Illustration', related_name='primary',
									on_delete=models.CASCADE, default=None)
	secondary = models.ForeignKey('Illustration', related_name='secondary',
									on_delete=models.CASCADE, default=None)
	relation_type = models.ForeignKey(IllustrationIllustrationRelationType, 
									on_delete=models.CASCADE, default=None)
	model_fields = ['primary','secondary']

	def __str__(self):
		try:
			m =  self.relation_type.name +' relation between ' 
			m += self.secondary.caption+' and '
			m += self.primary.caption
		except:
			m='WARNING, could not create string for '
			m+='IllustrationIllustrationRelation'
			print(m)
			return ''
		return m
