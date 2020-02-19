from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.template.loader import render_to_string
from .models import Person, PersonLocationRelation, LocationRelation
from .models import PersonTextRelation, PersonTextRelationRole 
from .models import PersonIllustrationRelation, PersonIllustrationRelationRole
from .models import PublisherManager
from catalogue.models import Text, Illustration, Publisher 
from catalogue.forms import PublisherWidget
from django_select2.forms import Select2Widget,ModelSelect2Widget
import json
from locations.models import UserLoc
from locations.forms import LocationWidget, LocationsWidget


class PersonWidget(ModelSelect2Widget):
	model = Person
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return Person.objects.all().order_by('name')


class LocationRelationWidget(ModelSelect2Widget):
	model = LocationRelation 
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return LocationRelation.objects.all().order_by('name')

class TextWidget(ModelSelect2Widget):
	model = Text
	search_fields = ['title__icontains']

	def label_from_instance(self,obj):
		return obj.title

	def get_queryset(self):
		return Text.objects.all().order_by('title')


class IllustrationWidget(ModelSelect2Widget):
	model = Illustration
	search_fields = ['caption__icontains']

	def label_from_instance(self,obj):
		return obj.caption

	def get_queryset(self):
		return Illustration.objects.all().order_by('caption')


class PersonTextRelationRoleWidget(ModelSelect2Widget):
	model = PersonTextRelationRole
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return PersonTextRelationRole.objects.all()

class PersonIllustrationRelationRoleWidget(ModelSelect2Widget):
	model = PersonIllustrationRelationRole
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return PersonIllustrationRelationRole.objects.all()

class PersonTextRelationRoleForm(ModelForm):
	name= forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	class Meta:
		model = PersonTextRelationRole
		fields = ['name']

class PersonIllustrationRelationRoleForm(ModelForm):
	name= forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	class Meta:
		model = PersonIllustrationRelationRole
		fields = ['name']


class PublisherManagerForm(ModelForm):
	manager = forms.ModelChoiceField(
		queryset=Person.objects.all(),
		widget=PersonWidget(
			attrs={'data-placeholder':'Select role... e.g., author',
			'style':'width:100%;','class':'searching',
			'data-minimum-input-length':'1'}))
	publisher = forms.ModelChoiceField(
		queryset=Publisher.objects.all().order_by('name'),
		widget=PublisherWidget(attrs={'data-placeholder':'Select publisher..',
			'style':'width:100%;','class':'searching'}),
		required = False
		)
	class Meta:
		model = PublisherManager
		fields = ['manager','publisher']

publisher_formset = inlineformset_factory(
	Person,PublisherManager,
	form = PublisherManagerForm, extra=1)


class PersonTextRelationForm(ModelForm):
	'''Form to add a person location relation'''
	text = forms.ModelChoiceField(
		queryset=Text.objects.all(),
		widget=TextWidget(
			attrs={'data-placeholder':'Select text by title...',
			'style':'width:100%;','class':'searching'}))
	role = forms.ModelChoiceField(
		queryset=PersonTextRelationRole.objects.all(),
		widget=PersonTextRelationRoleWidget(
			attrs={'data-placeholder':'Select role... e.g., author',
			'style':'width:100%;','class':'searching',
			'data-minimum-input-length':'0'}))

	class Meta:
		model = PersonTextRelation
		fields = 'text,role'
		fields = fields.split(',')

text_formset = inlineformset_factory(
	Person,PersonTextRelation,
	form = PersonTextRelationForm, extra=1)


class PersonIllustrationRelationForm(ModelForm):
	'''Form to add a person location relation'''
	illustration = forms.ModelChoiceField(
		queryset=Illustration.objects.all(),
		widget=IllustrationWidget(
			attrs={'data-placeholder':'Select illustration by title...',
			'style':'width:100%;','class':'searching'}))
	role = forms.ModelChoiceField(
		queryset=PersonIllustrationRelationRole.objects.all(),
		widget=PersonIllustrationRelationRoleWidget(
			attrs={'data-placeholder':'Select role... e.g., illustrator',
			'style':'width:100%;','class':'searching',
			'data-minimum-input-length':'0'}))

	class Meta:
		model = PersonIllustrationRelation
		fields = 'illustration,role'
		fields = fields.split(',')

illustration_formset = inlineformset_factory(
	Person,PersonIllustrationRelation,
	form = PersonIllustrationRelationForm, extra=1)


class LocationRelationForm(ModelForm):
	name= forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	class Meta:
		model = LocationRelation
		fields = ['name']

class PersonLocationRelationForm(ModelForm):
	'''Form to add a person location relation'''
	spec_choices= [('d','day'),('m','month'),('y','year'),('c','century')]
	attrs={'class':'form-control','type':'date'}
	location = forms.ModelChoiceField(
		queryset=UserLoc.objects.all().order_by('name'),
		widget=LocationWidget(attrs={'data-placeholder':'Select location...',
			'style':'width:100%;','class':'searching'}))
	relation = forms.ModelChoiceField(
		queryset=PersonIllustrationRelationRole.objects.all(),
		widget=LocationRelationWidget(
			attrs={'data-placeholder':'e.g. travel',
			'style':'width:100%;','class':'searching',
			'data-minimum-input-length':'0'}))
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
