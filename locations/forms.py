from django import forms
from django.forms import ModelForm, inlineformset_factory, Form
from django.db.utils import IntegrityError
from .models import GeoLoc, UserLoc,LocType, GeoLocsRelation
from .widgets import GeoLocationWidget, GeoLocationsWidget, CountryWidget

class UserLocForm(ModelForm):
	name = forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	geolocs= forms.ModelMultipleChoiceField(
		queryset=GeoLoc.objects.all().order_by('name'),
		widget=GeoLocationsWidget(attrs={'data-placeholder':'Select location...',
			'style':'width:100%;','class':'searching'}),
		required = False)
	notes = forms.CharField(widget=forms.Textarea(
		attrs={'style':'width:100%','rows':3}),
		required=False)

	# saving m2m on the other model (that does not define the m2m field)
	# source: https://stackoverflow.com/questions/2216974/django-modelform-for-many-to-many-fields
	def __init__(self, *args, **kwargs):
		if kwargs.get('instance'):
			initial = kwargs.setdefault('initial',{})
			initial['geolocs'] = [gl.pk for gl in kwargs['instance'].geoloc_set.all()]
		forms.ModelForm.__init__(self, *args, **kwargs)

	def save(self, commit=True):
		instance = forms.ModelForm.save(self,False)
		osm = self.save_m2m
		def save_m2m():
			osm()
			instance.geoloc_set.clear()
			instance.geoloc_set.add(*self.cleaned_data['geolocs'])
		self.save_m2m = save_m2m
		if commit:
			instance.save()
			self.save_m2m()
		return instance
	#---

	class Meta:
		model = UserLoc
		fields = 'name,geolocs,loc_type,loc_precision,status,notes'.split(',')

class GeoLocForm(ModelForm):
	name = forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	latitude = forms.DecimalField(widget=forms.NumberInput(
		attrs={'style':'width:100%','placeholder':'latitude coordinate'}),
		required = False)
	longitude = forms.DecimalField(widget=forms.NumberInput(
		attrs={'style':'width:100%','placeholder':'longitude coordinate'}),
		required = False)
	contained_by_country= forms.ModelChoiceField(
		queryset= GeoLoc.objects.filter(location_type='COUNTRY'),
		widget=CountryWidget(attrs={
			'data-placeholder':'select the country containing this location...',
			'style':'width:100%;','class':'searching'}),
		required = False)
	notes = forms.CharField(widget=forms.Textarea(
		attrs={'style':'width:100%','rows':3}),
		required=False)

	class Meta:
		model = GeoLoc
		fields = 'name,location_type,latitude,longitude,contained_by_country,notes'.split(',')

	def save(self, commit=True):
		country = self.cleaned_data['contained_by_country']
		print(self.cleaned_data, 1999)
		l = forms.ModelForm.save(self,commit)
		lt_dict = dict([(lt.name,lt) for lt in LocType.objects.all()])
		ul = UserLoc(name=l.name,loc_precision='E',status='NF',
			loc_type= lt_dict[l.location_type.lower()])
		glr = GeoLocsRelation(container=country,contained=l)
		if commit:
			ul.save()
			l.user_locs.add(ul)
			glr.save()
		return ul

class FastLocForm(Form):
	location = forms.ModelChoiceField(
		queryset=GeoLoc.objects.all().order_by('name'),
		widget=GeoLocationWidget(attrs={'data-placeholder':'Select location...',
			'style':'width:100%;','class':'searching'}))
	
	def save(self, commit = True):
		data = self.cleaned_data
		l = data['location']
		lt_dict = dict([(lt.name,lt) for lt in LocType.objects.all()])
		ul = UserLoc(name=l.name,loc_precision='E',status='NF',
			loc_type= lt_dict[l.location_type.lower()])
		if userloc_exists(ul,l): raise IntegrityError('location with name %s already exists' %
			(ul.name))
		if commit:
			ul.save()
			l.user_locs.add(ul)

def userloc_exists(ul,l):
	existing_ul = UserLoc.objects.filter(name = ul.name)
	for location in existing_ul:
		gl =location.geoloc_set.all()
		if gl.count() == 0: return False
		if location.geoloc_set.all()[0] == l:
			if location.loc_type == ul.loc_type: return True
	return False
	
