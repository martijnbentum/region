from django import forms
from django.db.models import Q
from django.forms import ModelForm, inlineformset_factory, Form
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset
from django_select2.forms import ModelSelect2Widget
from .models import Language, Comment, Modelname
from .widgets import ModelnameWidget
from accounts.widgets import UserWidget
from django.contrib.auth import get_user_model

from locations.models import Location
from locations.widgets import LocationWidget, LocationCountryWidget

User = get_user_model()


class LanguageWidget(ModelSelect2Widget):
	model = Language
	search_fields = ['name__startswith']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return Language.objects.all().order_by('name')

def make_select2_attr(field_name = None, input_length = 2,
	data_placeholder = None):
	if field_name == None:field_name = 'name' 
	if not data_placeholder: 
		data_placeholder = 'Select by ' + field_name + ' ...'
	attr= {'attrs':{
		'data-placeholder':data_placeholder,
		'style':'width:100%',
		'class':'searching',
		'data-minimum-input-length':str(input_length)}} 
	return attr

dattr = {'attrs':{'style':'width:100%'}}
dchar = {'widget':forms.TextInput(**dattr),'required':False}
dchar_required = {'widget':forms.TextInput(**dattr),'required':True}
dtext = {'widget':forms.Textarea(
	attrs={'style':'width:100%; font-size: 80%;','rows':9}),
	'required':False}
dselect2 = make_select2_attr(input_length = 0)
dselect2n2 = make_select2_attr(input_length = 2)



class CommentForm(ModelForm):
	subject= forms.CharField(**dchar)
	comment=forms.CharField(**dtext)

	class Meta:
		model =Comment
		fields='subject,comment,fixed'.split(',')


class TimelineForm(Form):
	c = Q(location_type__name= 'country')
	r = Q(location_type__name= 'region')
	location1= forms.ModelChoiceField(
		queryset = Location.objects.all(),
		widget=LocationCountryWidget(**dselect2),
		required = False)
	location2= forms.ModelChoiceField(
		queryset = Location.objects.all(),
		widget=LocationCountryWidget(**dselect2),
		required = False)
	location3= forms.ModelChoiceField(
		queryset = Location.objects.all(),
		widget=LocationCountryWidget(**dselect2),
		required = False)
	location4= forms.ModelChoiceField(
		queryset = Location.objects.all(),
		widget=LocationCountryWidget(**dselect2),
		required = False)
	model_name1= forms.ModelChoiceField(
		queryset=Modelname.objects.all().order_by('model_name'),
		widget=ModelnameWidget(**dselect2),
		required = False)
	model_name2= forms.ModelChoiceField(
		queryset=Modelname.objects.all().order_by('model_name'),
		widget=ModelnameWidget(**dselect2),
		required = False)
	model_name3= forms.ModelChoiceField(
		queryset=Modelname.objects.all().order_by('model_name'),
		widget=ModelnameWidget(**dselect2),
		required = False)
	model_name4= forms.ModelChoiceField(
		queryset=Modelname.objects.all().order_by('model_name'),
		widget=ModelnameWidget(**dselect2),
		required = False)

	

