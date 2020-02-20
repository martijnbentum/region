from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.template.loader import render_to_string
from .models import Person, PersonLocationRelation, LocationRelation
from .models import PersonTextRelation, PersonTextRelationRole 
from .models import PersonIllustrationRelation, PersonIllustrationRelationRole
from .models import PublisherManager, Pseudonym
from catalogue.models import Text, Illustration, Publisher 
from catalogue.widgets import TextWidget, PublisherWidget, IllustrationWidget
from locations.models import UserLoc
from locations.forms import LocationWidget, LocationsWidget
from .widgets import PersonIllustrationRelationRoleWidget, LocationRelationWidget
from .widgets import PersonTextRelationRoleWidget, PersonWidget, PseudonymsWidget


class PseudonymForm(ModelForm):
	name= forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	class Meta:
		model = Pseudonym
		fields = ['name']


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
		queryset=LocationRelation.objects.all(),
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
	pseudonym = forms.ModelMultipleChoiceField(
		queryset=Pseudonym.objects.all().order_by('name'),
		widget=PseudonymsWidget(attrs={'data-placeholder':'Select pseudonym(s)',
			'style':'width:100%;','class':'searching',
			'data-minimum-input-length':'1'}),
		required = False
		)

	class Meta:
		model = Person
		m = 'first_name,last_name,sex,birth_year,death_year'
		m +=',birth_place,death_place,pseudonym'
		fields = m.split(',')

def bound_form(request, id):
	person = get_object_or_404(Person, id=id)
	form = PersonForm(instance=person) 
	return render_to_response('edit_person.html', {'form':form})
