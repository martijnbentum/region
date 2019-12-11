from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.template.loader import render_to_string
from .models import Date, Language, Location, Person
from .models import PersonLocationRelation, Text
from django_select2.forms import Select2MultipleWidget, Select2Widget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Fieldset,HTML
from crispy_forms.layout import LayoutObject, TEMPLATE_PACK


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


class PersonLocationRelationForm(ModelForm):
	'''Form to add a person location relation'''
	spec_choices= [('d','day'),('m','month'),('y','year'),('c','century')]
	attrs={'class':'form-control','type':'date'}
	location = forms.ModelChoiceField(
		queryset=Location.objects.order_by('name'),
		widget=Select2Widget,
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

class formsethelper(FormHelper):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.form_method = 'POST'
		self.layout= Layout(
			Row(
				Column(Field('location', style ='width:100%'),css_class='form-group col-md-6 mb-0'),
				Column('relation', css_class='form-group col-md-6 mb-0'),
				css_class='from-row'
			),
			Row(
				Column('start_date', css_class='form-group col-md-4 mb-0'),
				Column('start_spec', css_class='form-group col-md-2 mb-0'),
				Column('end_date', css_class='form-group col-md-4 mb-0'),
				Column('end_spec', css_class='form-group col-md-2 mb-0'),
				css_class='from-row'
			),
			)

location_formset = inlineformset_factory(
	Person,PersonLocationRelation,
	form = PersonLocationRelationForm, extra=1)
helper = formsethelper()

class PersonForm(ModelForm):
	'''form to add a person'''
	spec_choices= [('d','day'),('m','month'),('y','year'),('c','century')]
	attrs={'class':'form-control','type':'date'}
	date_of_birth = forms.DateField(required=False, 
		widget = forms.DateInput(format=('%d %m $y'), attrs=attrs))
	date_of_death = forms.DateField(required=False,
		widget = forms.DateInput(format=('%d %m $y'), attrs=attrs))
	place_of_birth= forms.ModelChoiceField(
		queryset=Location.objects.order_by('name'),
		widget=Select2Widget,
		required = False
		)
	place_of_death= forms.ModelChoiceField(
		queryset=Location.objects.order_by('name'),
		widget=Select2Widget,
		required = False
		)
	birth_spec = forms.ChoiceField(choices = spec_choices, 
		label= '&nbsp;', required = False)
	death_spec = forms.ChoiceField(choices = spec_choices, 	
		label = '&nbsp;', required = False)


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.add_input(
			Submit('submit', 'Save', css_class='btn-success'))
		self.helper.form_method = 'POST'
		# self.helper.form_class= 'form-horizontal'

		self.helper.layout= Layout(
			'first_name',
			Row(
				Column('last_name', css_class='form-group col-md-10 mb-0'),
				Column('sex', css_class='form-group col-md-2 mb-0'),
				css_class='from-row'
			),
			HTML('<hr class="mt-0 mb-4">'),
			Row(
				Column('date_of_birth', css_class='form-group col-md-4 mb-0'),
				Column('birth_spec', css_class='form-group col-md-2 mb-0'),
				Column('date_of_death', css_class='form-group col-md-4 mb-0'),
				Column('death_spec', css_class='form-group col-md-2 mb-0'),
				css_class='from-row'
			),
			Row(
				Column(Field('place_of_birth',style='width:100%'), css_class='form-group col-md-6 mb-0'),
				Column(Field('place_of_death',style='width:100%'), css_class='form-group col-md-6 mb-0'),
				css_class='from-row'
			),
			Formset('locations'),
			)

	class Meta:
		model = Person
		m = 'first_name,last_name,sex,notes'
		fields = m.split(',')

def bound_form(request, id):
	person = get_object_or_404(Person, id=id)
	form = PersonForm(instance=person) 
	return render_to_response('edit_person.html', {'form':form})
# location_name = forms.CharField(label='location name',max_length= 200)


