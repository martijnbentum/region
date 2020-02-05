from django.db import models
from django.utils import timezone
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


class Language(models.Model, info):
	name = models.CharField(max_length=100, unique = True)
	iso = models.CharField(max_length=3,null=True,blank=True)

	def __str__(self):
		return self.name
# Create your models here.
