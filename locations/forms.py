from django import forms
from django.forms import ModelForm, inlineformset_factory, Form
from django.db.utils import IntegrityError
from .models import GeoLoc, UserLoc,LocType, GeoLocsRelation
from .widgets import GeoLocationWidget, GeoLocationsWidget, CountryWidget, RegionWidget
from .widgets import GeoLocWidget, GeoLocVerboseWidget

class UserLocForm(ModelForm):
	'''form to add a userloc.'''
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
	'''form to add or edit a geoloc.'''
	name = forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	latitude = forms.DecimalField(widget=forms.NumberInput(
		attrs={'style':'width:100%','placeholder':'latitude coordinate'}),
		required = False)
	longitude = forms.DecimalField(widget=forms.NumberInput(
		attrs={'style':'width:100%','placeholder':'longitude coordinate'}),
		required = False)
	notes = forms.CharField(widget=forms.Textarea(
		attrs={'style':'width:100%','rows':3}),
		required=False)
	#needed to make the select2 field work in tabs
	placeholder= forms.ModelChoiceField(
		queryset= GeoLoc.objects.all(),
		widget=GeoLocationWidget(attrs={
			'data-placeholder':'..',
			'style':'width:100%;','class':'searching'}),
		required = False)

	class Meta:
		model = GeoLoc
		fields = 'name,location_type,latitude,longitude,notes'.split(',')


class FastLocForm(Form):
	'''create a userloc based on a geoloc.
	there is a large database of geolocs, only a subset had a corresponding userloc.
	userlocs are used as locations. This form is used to add locations form the database.
	'''
	location = forms.ModelChoiceField(
		queryset=GeoLoc.objects.all().order_by('name'),
		widget=GeoLocationWidget(attrs={'data-placeholder':'Select location...',
			'style':'width:100%;','class':'searching'}))
	
	def save(self, commit = True):
		data = self.cleaned_data
		l = data['location']
		lt_dict = dict([(lt.name,lt) for lt in LocType.objects.all()])
		ul = UserLoc(name=l.name,loc_precision='exact',status='non-fiction',
			loc_type= lt_dict[l.location_type.lower()])
		if userloc_exists(ul,l): raise IntegrityError('location with name %s already exists' %
			(ul.name))
		if commit:
			ul.save()
			l.user_locs.add(ul)

class GeoLocRelationForm(ModelForm):
	'''Form to add a geo location relation.
	'''
	container = forms.ModelChoiceField(
		queryset= GeoLoc.objects.all(),
		widget=GeoLocVerboseWidget(attrs={
			'data-placeholder':'select the location containing this location...',
			'style':'width:100%;','class':'searching'}),
		required = False)

	class Meta:
		model = GeoLocsRelation
		fields = ['container','contained']

geoloc_relation_formset = inlineformset_factory(
	GeoLoc,GeoLocsRelation,fk_name = 'contained',
	form = GeoLocRelationForm, extra=1)


def userloc_exists(ul,l):
	'''check whether there already exists a userloc for a specific geoloc.'''
	existing_ul = UserLoc.objects.filter(name = ul.name)
	for location in existing_ul:
		gl =location.geoloc_set.all()
		if gl.count() == 0: return False
		if location.geoloc_set.all()[0] == l:
			if location.loc_type == ul.loc_type: return True
	return False
	

def geoloc2userloc(gl):
	'''returns the userloc corresponding to a geoloc (if it exists).'''
	uls = gl.userloc_set.all()
	if uls.count() == 1: return uls[0]
	for ul in uls: 
		if ul.name == ul.name: return ul
	return None


# does not seem to work, have problems with the select2 field (doe snot show as select2 field)
# if i have a country / region tab
# also gave some error, now using geoloc_relation_formset

class GeoLocsCountryRelationForm(ModelForm):
	'''Form to add a geo location relation.
	'''
	container= forms.ModelChoiceField(
		queryset= GeoLoc.objects.filter(location_type='COUNTRY'),
		widget=CountryWidget(attrs={
			'data-placeholder':'select the country containing this location...',
			'style':'width:100%;','class':'searching'}),
		required = False)
	contained= forms.ModelChoiceField(
		queryset= GeoLoc.objects.all(),
		widget=GeoLocationWidget(attrs={
			'data-placeholder':'select the contained location...',
			'style':'width:100%;','class':'searching'}),
		required = False)

	class Meta:
		model = GeoLocsRelation
		fields = ['container','contained']

class GeoLocsRegionRelationForm(ModelForm):
	'''Form to add a geo location relation.
	'''
	container1 = forms.ModelChoiceField(
		queryset= GeoLoc.objects.filter(location_type='REGION'),
		widget=RegionWidget(attrs={
			'data-placeholder':'select the region containing this location...',
			'style':'width:100%;','class':'searching'}),
		required = False)

	class Meta:
		model = GeoLocsRelation
		fields = ['container','contained']



geolocrelation_country_formset = inlineformset_factory(
	GeoLoc,GeoLocsRelation,fk_name = 'contained',
	form = GeoLocsCountryRelationForm, extra=1)
geolocrelation_region_formset = inlineformset_factory(
	GeoLoc,GeoLocsRelation,fk_name = 'contained',
	form = GeoLocsRegionRelationForm, extra=1)

country_formset = inlineformset_factory(
	GeoLoc,GeoLocsRelation,fk_name = 'contained',
	form = GeoLocsCountryRelationForm, extra=1)
region_formset = inlineformset_factory(
	GeoLoc,GeoLocsRelation,fk_name = 'contained',
	form = GeoLocsRegionRelationForm, extra=1)





