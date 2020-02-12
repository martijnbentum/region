from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.template.loader import render_to_string
from .models import Person, PersonLocationRelation 
from catalogue.models import Date, Language 
from django_select2.forms import Select2Widget,HeavySelect2Widget,ModelSelect2Widget
import json
from locations.models import UserLoc
from locations.forms import LocationWidget, LocationsWidget


class PersonLocationRelationForm(ModelForm):
	'''Form to add a person location relation'''
	spec_choices= [('d','day'),('m','month'),('y','year'),('c','century')]
	attrs={'class':'form-control','type':'date'}
	location = forms.ModelChoiceField(
		queryset=UserLoc.objects.all().order_by('name'),
		widget=LocationWidget(attrs={'data-placeholder':'Select location...',
			'style':'width:100%;','class':'searching'}))
	start_year= forms.IntegerField(widget=forms.NumberInput(
		attrs={'style':'width:100%', 'placeholder':'year'}),
	required = False)
	end_year= forms.IntegerField(widget=forms.NumberInput(
		attrs={'style':'width:100%','placeholder':'year'}),
	required = False)

	class Meta:
		model = PersonLocationRelation
		fields = 'location,relation,start_year,end_year'
		fields = fields.split(',')


location_formset = inlineformset_factory(
	Person,PersonLocationRelation,
	form = PersonLocationRelationForm, extra=1)


class PersonForm(ModelForm):
	'''form to add a person'''
	attrs={'class':'form-control','type':'date'}

	birth_place= forms.ModelChoiceField(
		queryset=UserLoc.objects.all().order_by('name'),
		widget=LocationWidget(attrs={'data-placeholder':'Select location...',
			'style':'width:100%;','class':'searching'}),
		required = False)
	death_place= forms.ModelChoiceField(
		queryset=UserLoc.objects.all().order_by('name'),
		widget=LocationWidget(attrs={'data-placeholder':'Select location...',
			'style':'width:100%;','class':'searching'}),
		required = False)
	first_name= forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	last_name= forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	birth_year= forms.IntegerField(widget=forms.NumberInput(
		attrs={'style':'width:100%', 'placeholder':'year of birth'}),
		required = False)
	death_year= forms.IntegerField(widget=forms.NumberInput(
		attrs={'style':'width:100%','placeholder':'year of death'}),
		required = False)

	class Meta:
		model = Person
		m = 'first_name,last_name,sex,birth_year,death_year'
		m +=',birth_place,death_place'
		fields = m.split(',')

def bound_form(request, id):
	person = get_object_or_404(Person, id=id)
	form = PersonForm(instance=person) 
	return render_to_response('edit_person.html', {'form':form})
