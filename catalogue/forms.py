from django import forms
from django.forms import ModelForm
from .models import Date, Language, Location, Person, PersonLocationRelation, Text
from django_select2.forms import Select2MultipleWidget, Select2Widget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field


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
				Column('start_date', css_class='form-group col-md-6 mb-0'),
				Column('end_date', css_class='form-group col-md-6 mb-0'),
				css_class='from-row'
			),
			'start_spec',
			'end_spec',
			)

	class Meta:
		model = Date
		fields = 'start_date,end_date,start_spec,end_spec'.split(',')
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
	location = forms.ModelChoiceField(
		queryset=Location.objects.order_by('name'),
		widget=Select2Widget,
		required = False
		)

	person = forms.ModelChoiceField(
		queryset=Person.objects.order_by('last_name'),
		widget=Select2Widget,
		required = False
		)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.add_input(
			Submit('submit', 'Save', css_class='btn-success'))
		self.helper.form_method = 'POST'
		self.helper.layout= Layout(
			'person',
			Field('location', style='width:100%'),
			'relation',
			'date',
			)

	class Meta:
		model = PersonLocationRelation
		fields = 'person,location,relation,date'.split(',')

class PersonForm(ModelForm):
	'''form to add a person'''
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.add_input(
			Submit('submit', 'Save', css_class='btn-success'))
		self.helper.form_method = 'POST'

		self.helper.layout= Layout(
			Row(
				Column('first_name', css_class='form-group col-md-6 mb-0'),
				Column('last_name', css_class='form-group col-md-6 mb-0'),
				css_class='from-row'
			),
			'gender'
			)

	class Meta:
		model = Person
		m = 'first_name,last_name,gender,notes'
		fields = m.split(',')
		attrs={'class':'form-control',
			'type':'date'}
		widgets = {
			'date_of_birth': forms.DateInput(
				format=('%d %m $Y'),
				attrs= attrs
				),
			'date_of_death': forms.DateInput(
				format=('%d %m $Y'),
				attrs= attrs
				)
		}
		labels = {'date_spec':'date specificity'}

def bound_form(request, id):
	person = get_object_or_404(Person, id=id)
	form = PersonForm(instance=person) 
	return render_to_response('edit_person.html', {'form':form})
# location_name = forms.CharField(label='location name',max_length= 200)


