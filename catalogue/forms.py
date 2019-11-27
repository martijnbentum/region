from django import forms
from django.forms import ModelForm
from .models import Language, Location, Person, Text
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
	

class PersonForm(ModelForm):#forms.Form):
	'''Form to add a person'''
	residence = forms.ModelChoiceField(
		queryset=Location.objects.order_by('name'),
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
			Row(
				Column('first_name', css_class='form-group col-md-6 mb-0'),
				Column('last_name', css_class='form-group col-md-6 mb-0'),
				css_class='from-row'
			),
			'pseudonyms',
			'gender',
			Row(
				Column('date_of_birth', css_class='form-group col-md-6 mb-0'),
				Column('date_of_death', css_class='form-group col-md-6 mb-0'),
				css_class='from-row'
			),
			'date_spec',
			Field('residence', style='width:100%')
			)

	class Meta:
		model = Person
		m = 'first_name,last_name,pseudonyms'
		m += ',gender,date_spec,date_of_birth,date_of_death,residence'#,notes'
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


