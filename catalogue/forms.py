from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.template.loader import render_to_string
from .models import Date, Language, Location, Person
from .models import PersonLocationRelation, Text
from django_select2.forms import Select2Widget,HeavySelect2Widget,ModelSelect2Widget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Fieldset,HTML
from crispy_forms.layout import LayoutObject, TEMPLATE_PACK
import json


class TextForm(ModelForm):
	'''Form to add a text'''
	language = forms.ModelMultipleChoiceField(
		queryset=Language.objects.order_by('name'),
		widget=Select2Widget,
		required = False
		)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.layout= Layout(
			'title',
			Field('language', style='width:100%',),
			Row(
				Column('genre', css_class='form-group col-md-6 mb-0'),
				Column('upload', css_class='form-group col-md-6 mb-0'),
				css_class='from-row'
			),
			'notes'
			)

	class Meta:
		model = Text
		m = 'title,language,genre,upload,notes'
		fields = m.split(',')

class Formset(LayoutObject):
	template = "catalogue/formset.html"

	def __init__(self, formset_name_in_context, template=None):
		self.formset_name_in_context = formset_name_in_context
		self.fields = []
		if template:
			self.template = template

	def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
		print(context)
		formset = context[self.formset_name_in_context]
		render_to_string(self.template,{'formset':formset})

class LocationForm(ModelForm):#forms.Form):
	'''Form to add a location'''
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.layout= Layout(
			'name',
			Row(
				Column('status', css_class='form-group col-md-6 mb-0'),
				Column('location_type', css_class='form-group col-md-6 mb-0'),
				css_class='from-row'
			),
			Row(
				Column('latitude', css_class='form-group col-md-6 mb-0'),
				Column('longitude', css_class='form-group col-md-6 mb-0'),
				css_class='from-row'
			),
			'coordinates_polygon',
			'notes'
			)

	class Meta:
		model = Location
		m = 'name,status,location_type'
		m += ',latitude,longitude,notes,coordinates_polygon'
		fields = m.split(',')
	

class DateForm(ModelForm):
	'''form to add a person'''

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.add_input(
			Submit('submit', 'Save', css_class='btn-success'))
		self.helper.form_method = 'POST'

		self.helper.layout= Layout(
			Row(
				Column('start', css_class='form-group col-md-6 mb-0'),
				Column('end', css_class='form-group col-md-6 mb-0'),
				css_class='from-row'
			),
			'start_specificity',
			'end_specificity',
			)

	class Meta:
		model = Date
		fields = 'start,end,start_specificity,end_specificity'.split(',')
		attrs={'class':'form-control',
			'type':'date'}
		widgets = {
			'date_start': forms.DateInput(
				format=('%d %m $Y'),
				attrs= attrs
				),
			'date_end': forms.DateInput(
				format=('%d %m $Y'),
				attrs= attrs
				)
		}
		labels = {'start_spec':'start specificity',
			'end_spec':'end specificity'}


class LocationWidget(ModelSelect2Widget):
	model = Location
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return Location.objects.all().order_by('name')

class PersonLocationRelationForm(ModelForm):
	'''Form to add a person location relation'''
	spec_choices= [('d','day'),('m','month'),('y','year'),('c','century')]
	attrs={'class':'form-control','type':'date'}
	location = forms.ModelChoiceField(
		queryset=Location.objects.all().order_by('name'),
		widget=LocationWidget(attrs={'data-placeholder':'Select location...',
			'style':'width:100%;','class':'searching'}),
		required = False
		)
	start_date = forms.DateField(required=False,
		widget = forms.DateInput(format=('%d %m $Y'), attrs=attrs))
	end_date = forms.DateField(required=False,
		widget = forms.DateInput(format=('%d %m $y'), attrs=attrs))
	start_spec = forms.ChoiceField(choices = spec_choices, 
		label= '&nbsp;', required = False)
	end_spec = forms.ChoiceField(choices = spec_choices, 	
		label = '&nbsp;', required = False)

	class Meta:
		model = PersonLocationRelation
		fields = 'location,relation,start_date,start_spec,end_date,end_spec'
		fields = fields.split(',')


location_formset = inlineformset_factory(
	Person,PersonLocationRelation,
	form = PersonLocationRelationForm, extra=1)

class PersonForm(ModelForm):
	'''form to add a person'''
	spec_choices= [('d','day'),('m','month'),('y','year'),('c','century')]
	attrs={'class':'form-control','type':'date'}
	date_of_birth = forms.DateField(required=False, 
		widget = forms.DateInput(format=('%d %m $y'), attrs=attrs))
	date_of_death = forms.DateField(required=False,
		widget = forms.DateInput(format=('%d %m $y'), attrs=attrs))
	place_of_birth= forms.ModelChoiceField(
		queryset=Location.objects.all().order_by('name'),
		widget=LocationWidget(attrs={'data-placeholder':'Select location...',
			'style':'width:100%;','class':'searching'}),
		# widget=HeavySelect2Widget(data_view = 'catalogue:heavy_data'),
		required = False
		)
	place_of_death= forms.ModelChoiceField(
		queryset=Location.objects.all().order_by('name'),
		widget=LocationWidget(attrs={'data-placeholder':'Select location...',
			'style':'width:100%;','class':'searching'}),
		# widget=HeavySelect2Widget(data_view = 'catalogue:heavy_data'),
		required = False
		)
	birth_spec = forms.ChoiceField(choices = spec_choices, 
		label= '&nbsp;', required = False)
	death_spec = forms.ChoiceField(choices = spec_choices, 	
		label = '&nbsp;', required = False)

	class Meta:
		model = Person
		m = 'first_name,last_name,sex,date_of_birth,birth_spec,date_of_death'
		m +=',death_spec,place_of_birth,place_of_death'
		fields = m.split(',')

def bound_form(request, id):
	person = get_object_or_404(Person, id=id)
	form = PersonForm(instance=person) 
	return render_to_response('edit_person.html', {'form':form})


