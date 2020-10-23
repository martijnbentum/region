from django import forms
from django.forms import ModelForm, inlineformset_factory, Form, modelform_factory
from django.db.utils import IntegrityError
from .models import Location, LocationRelation, LocationType, LocationStatus, LocationPrecision
from .models import Color,Figure
from .widgets import LocationWidget, LocationsWidget, LocationPrecisionWidget 
from .widgets import LocationVerboseWidget, LocationTypeWidget, LocationStatusWidget
from .widgets import ColorWidget
from utilities.forms import make_select2_attr

dattr = {'attrs':{'style':'width:100%'}}
dchar = {'widget':forms.TextInput(**dattr),'required':False}
dchar_required = {'widget':forms.TextInput(**dattr),'required':True}
dtext = {'widget':forms.Textarea(attrs={'style':'width:100%','rows':3}),'required':False}
dselect2 = make_select2_attr(input_length = 0)
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
		queryset=LocationStatus.objects.all().order_by('name'),
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


class FigureForm(ModelForm):
	'''form to add or edit a figure.'''
	name = forms.CharField(**dchar_required)
	description= forms.CharField(**dtext)
	color = forms.ModelChoiceField(
		queryset=Color.objects.all().order_by('color'),
		widget=ColorWidget(**dselect2),
		required=False)
	start_date= forms.CharField(**dchar_required)
	end_date= forms.CharField(**dchar_required)
	district_number= forms.IntegerField(widget=forms.NumberInput(
		attrs={'style':'width:100%'}),
		required = False)
	city = forms.CharField(**dchar_required)

	class Meta:
		model = Figure
		fields = 'name,description,color,start_date,end_date,district_number,city,geojson'
		fields = fields.split(',')

class ColorForm(ModelForm):
	name = forms.CharField(**dchar_required)

	class Meta:
		model = Color
		fields = ['color','name']

