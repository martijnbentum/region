from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.template.loader import render_to_string
from .models import Person, PersonLocationRelation 
from catalogue.models import Date, Language 
from django_select2.forms import Select2Widget,HeavySelect2Widget,ModelSelect2Widget
import json
from locations.models import UserLoc
from locations.forms import LocationWidget


class PersonLocationRelationForm(ModelForm):
	'''Form to add a person location relation'''
	spec_choices= [('d','day'),('m','month'),('y','year'),('c','century')]
	attrs={'class':'form-control','type':'date'}
	location = forms.ModelChoiceField(
		queryset=UserLoc.objects.all().order_by('name'),
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
		queryset=UserLoc.objects.all().order_by('name'),
		widget=LocationWidget(attrs={'data-placeholder':'Select location...',
			'style':'width:100%;','class':'searching'}),
		# widget=HeavySelect2Widget(data_view = 'catalogue:heavy_data'),
		required = False
		)
	place_of_death= forms.ModelChoiceField(
		queryset=UserLoc.objects.all().order_by('name'),
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
