from django import forms
from django.forms import ModelForm, inlineformset_factory, Form, modelform_factory
from django.db.utils import IntegrityError
from .models import Location, LocationRelation, LocationType, LocationStatus, LocationPrecision
from .widgets import LocationWidget, LocationsWidget, LocationPrecisionWidget 
from .widgets import LocationVerboseWidget, LocationTypeWidget, LocationStatusWidget

dattr = {'attrs':{'style':'width:100%'}}
dchar = {'widget':forms.TextInput(**dattr),'required':False}
dchar_required = {'widget':forms.TextInput(**dattr),'required':True}
dtext = {'widget':forms.Textarea(attrs={'style':'width:100%','rows':3}),'required':False}
dselect2 = {'attrs':{'data-placeholder':'Select by name...','style':'width:100%',
	'class':'searching'}}
mft = {'fields':('name',),'widgets':{'name':forms.TextInput(dattr)}}


def create_simple_form(name):
	'''Create a simple model form based on the Model name. 
	Form is appended to model name
	Assumes the form only has a name field.
	'''
	exec(name + 'Form = modelform_factory('+name+',**mft)',globals())

#create simple forms for the following models
names = 'LocationType,LocationStatus,LocationPrecision'
for name in names.split(','):
	create_simple_form(name)


class LocationForm(ModelForm):
	'''form to add or edit a location.'''
	name = forms.CharField(**dchar_required)
	location_type = forms.ModelChoiceField(
		queryset=LocationType.objects.all().order_by('name'),
		widget=LocationTypeWidget(**dselect2),
		required=False)
	location_status= forms.ModelChoiceField(
		queryset=LocationType.objects.all().order_by('name'),
		widget=LocationStatusWidget(**dselect2),
		required=False)
	location_precision= forms.ModelChoiceField(
		queryset=LocationPrecision.objects.all().order_by('name'),
		widget=LocationPrecisionWidget(**dselect2),
		required=False)
	latitude = forms.DecimalField(widget=forms.NumberInput(
		attrs={'style':'width:100%','placeholder':'latitude coordinate'}),
		required = False)
	longitude = forms.DecimalField(widget=forms.NumberInput(
		attrs={'style':'width:100%','placeholder':'longitude coordinate'}),
		required = False)
	notes = forms.CharField(**dtext)

	class Meta:
		model = Location
		fields = 'name,location_type,latitude,longitude,notes'
		fields += ',location_status,location_precision'
		fields = fields.split(',')


class FastLocForm(Form):
	'''create a userloc based on a geoloc.
	there is a large database of geolocs, only a subset had a corresponding userloc.
	userlocs are used as locations. This form is used to add locations form the database.
	'''
	location = forms.ModelChoiceField(
		queryset=Location.objects.all().order_by('name'),
		widget=LocationWidget(attrs={'data-placeholder':'Select location...',
			'style':'width:100%;','class':'searching'}))
	
	def save(self, commit = True):
		data = self.cleaned_data
		l = data['location']
		lt_dict = dict([(lt.name,lt) for lt in LocationType.objects.all()])
		'''
		ul = UserLoc(name=l.name,loc_precision='exact',status='non-fiction',
			loc_type= lt_dict[l.location_type.lower()])
		if userloc_exists(ul,l): raise IntegrityError('location with name %s already exists' %
			(ul.name))
		if commit:
			ul.save()
			l.user_locs.add(ul)
		'''

class LocationRelationForm(ModelForm):
	'''Form to add a location relation.
	'''
	container = forms.ModelChoiceField(
		queryset= Location.objects.all(),
		widget=LocationVerboseWidget(attrs={
			'data-placeholder':'select the location containing this location...',
			'style':'width:100%;','class':'searching'}),
		required = False)

	class Meta:
		model = LocationRelation
		fields = ['container','contained']

location_relation_formset = inlineformset_factory(
	Location,LocationRelation,fk_name = 'contained',
	form = LocationRelationForm, extra=1)




