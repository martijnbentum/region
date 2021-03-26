from django import forms
from django.forms import ModelForm, inlineformset_factory, modelform_factory
from .models import Person, PersonLocationRelation, PersonLocationRelationType
from .models import PersonTextRelation, PersonTextRelationRole 
from .models import PersonIllustrationRelation, PersonIllustrationRelationRole
from .models import PublisherManager, Pseudonym, PersonMovementRelation
from .models import PersonMovementRelationRole, Movement, MovementType
from .models import PersonPeriodicalRelationRole,PersonPeriodicalRelation
from persons.models import PersonPersonRelation, PersonPersonRelationType
from catalogue.models import Text, Illustration, Publisher, Periodical
from catalogue.widgets import TextWidget, PublisherWidget, IllustrationWidget, PeriodicalWidget
from locations.models import Location
from locations.widgets import LocationWidget, LocationsWidget
from .widgets import PersonIllustrationRelationRoleWidget, PersonLocationRelationTypeWidget
from .widgets import PersonTextRelationRoleWidget, PersonWidget, PseudonymsWidget
from .widgets import PersonMovementRelationRoleWidget, MovementWidget, MovementTypeWidget
from .widgets import PersonPersonRelationTypeWidget, PersonPeriodicalRelationRoleWidget 
from utilities.forms import make_select2_attr 

#declaration of attributes to clean up form declaration
dattr = {'attrs':{'style':'width:100%'}}
dchar = {'widget':forms.TextInput(**dattr),'required':False}
dchar_required = {'widget':forms.TextInput(**dattr),'required':True}
dtext = {'widget':forms.Textarea(attrs={'style':'width:100%','rows':3}),'required':False}
dselect2 = make_select2_attr(input_length = 0)
dselect2n2 = make_select2_attr(input_length = 2)
mft = {'fields':('name',),'widgets':{'name':forms.TextInput(dattr)}}

def create_simple_form(name):
	'''Create a simple model form based on the Model name.
	'Form' is appended to model-name
	'''
	exec(name + 'Form = modelform_factory('+name+',**mft)',globals())

#create simple forms for the following models
names = 'Pseudonym,PersonPersonRelationType,PersonLocationRelationType,PersonTextRelationRole'
names += ',PersonIllustrationRelationRole,MovementType,PersonPeriodicalRelationRole'
names += ',PersonMovementRelationRole'
names = names.split(',')
for name in names:
	create_simple_form(name)


# --- main persons models ---

class PersonForm(ModelForm):
	'''form to add a person'''
	attrs={'class':'form-control','type':'date'}
	birth_place= forms.ModelChoiceField(
		queryset=Location.objects.all().order_by('name'),
		widget=LocationWidget(**dselect2n2),
		required = False)
	death_place= forms.ModelChoiceField(
		queryset=Location.objects.all().order_by('name'),
		widget=LocationWidget(**dselect2n2),
		required = False)
	first_name= forms.CharField(**dchar)
	last_name= forms.CharField(**dchar)
	birth_year= forms.IntegerField(widget=forms.NumberInput(
		attrs={'style':'width:100%', 'placeholder':'year of birth'}),
		required = False)
	death_year= forms.IntegerField(widget=forms.NumberInput(
		attrs={'style':'width:100%','placeholder':'year of death'}),
		required = False)
	pseudonym = forms.ModelMultipleChoiceField(
		queryset=Pseudonym.objects.all().order_by('name'),
		widget=PseudonymsWidget(**dselect2),
		required = False)

	class Meta:
		model = Person
		m = 'first_name,last_name,sex,birth_year,death_year'
		m +=',birth_place,death_place,pseudonym,approved,complete'
		fields = m.split(',')


class MovementForm(ModelForm):
	'''Form to add a movement (e.g. cultural literary political).'''
	location= forms.ModelChoiceField(
		queryset=Location.objects.all().order_by('name'),
		widget=LocationWidget(**dselect2n2),
		required = False)
	movement_type= forms.ModelChoiceField(
		queryset=MovementType.objects.all().order_by('name'),
		widget=MovementTypeWidget(**dselect2)) 
	name= forms.CharField(**dchar)
	founded= forms.IntegerField(widget=forms.NumberInput(**dattr),required=False)
	closure= forms.IntegerField(widget=forms.NumberInput(**dattr),required=False)
	notes = forms.CharField(**dtext)

	class Meta:
		model = Movement
		m = 'name,movement_type,location,founded,closure,notes,complete,approved'
		fields = m.split(',')


# --- relational forms ---

class PersonPersonRelationForm(ModelForm):
	'''Form to add a person person relation'''
	person1 = forms.ModelChoiceField(
		queryset=Person.objects.all(),
		widget=PersonWidget(**dselect2))
	person2 = forms.ModelChoiceField(
		queryset=Person.objects.all(),
		widget=PersonWidget(**dselect2))
	relation_type = forms.ModelChoiceField(
		queryset=PersonPersonRelationType.objects.all(),
		widget=PersonPersonRelationTypeWidget(**dselect2))

	class Meta:
		model = PersonPersonRelation
		fields = 'person2,relation_type'
		fields = fields.split(',')

#formsets are defined symmetrically to show relation on both sides of the relation
#relation between instances of same model are not really symmetrical
personperson_formset = inlineformset_factory(
	Person,PersonPersonRelation,fk_name = 'person1',
	form = PersonPersonRelationForm, extra=1)
personpersonr_formset = inlineformset_factory(
	Person,PersonPersonRelation,fk_name = 'person2',
	form = PersonPersonRelationForm, extra=0)


class PersonMovementRelationForm(ModelForm):
	'''Form to add a relation between a person and a movement.'''
	person = forms.ModelChoiceField(
		queryset=Person.objects.all(),
		widget=PersonWidget(**dselect2))
	movement= forms.ModelChoiceField(
		queryset=Movement.objects.all().order_by('name'),
		widget=MovementWidget(**dselect2))
	role = forms.ModelChoiceField(
		queryset=PersonMovementRelationRole.objects.all(),
		widget=PersonMovementRelationRoleWidget(**dselect2))

	class Meta:
		model = PersonMovementRelation
		fields = ['person','movement','role']

personmovement_formset = inlineformset_factory(
	Person,PersonMovementRelation,
	form = PersonMovementRelationForm, extra=1)
movementperson_formset = inlineformset_factory(
	Movement,PersonMovementRelation,
	form = PersonMovementRelationForm, extra=1)


class PublisherManagerForm(ModelForm):
	'''Form to add a relation (i.e. manage) between a person and a publisher.'''
	manager = forms.ModelChoiceField(
		queryset=Person.objects.all(),
		widget=PersonWidget(**dselect2))
	publisher = forms.ModelChoiceField(
		queryset=Publisher.objects.all().order_by('name'),
		widget=PublisherWidget(**dselect2))
	class Meta:
		model = PublisherManager
		fields = ['manager','publisher']

personpublisher_formset = inlineformset_factory(
	Person,PublisherManager,
	form = PublisherManagerForm, extra=1)
publisherperson_formset = inlineformset_factory(
	Publisher,PublisherManager,
	form = PublisherManagerForm, extra=1)


class PersonTextRelationForm(ModelForm):
	'''Form to add a person location relation'''
	person = forms.ModelChoiceField(
		queryset=Person.objects.all(),
		widget=PersonWidget(**dselect2))
	text = forms.ModelChoiceField(
		queryset=Text.objects.all(),
		widget=TextWidget(**dselect2))
	role = forms.ModelChoiceField(
		queryset=PersonTextRelationRole.objects.all(),
		widget=PersonTextRelationRoleWidget(**dselect2))
	published_under = forms.CharField(**dchar)

	class Meta:
		model = PersonTextRelation
		fields = 'person,text,role,published_under'
		fields = fields.split(',')

persontext_formset = inlineformset_factory(
	Person,PersonTextRelation,
	form = PersonTextRelationForm, extra=1)
textperson_formset = inlineformset_factory(
	Text,PersonTextRelation,
	form = PersonTextRelationForm, extra=1)


class PersonIllustrationRelationForm(ModelForm):
	'''Form to add a person illustration relation'''
	person = forms.ModelChoiceField(
		queryset=Person.objects.all(),
		widget=PersonWidget(**dselect2))
	illustration = forms.ModelChoiceField(
		queryset=Illustration.objects.all(),
		widget=IllustrationWidget(**dselect2))
	role = forms.ModelChoiceField(
		queryset=PersonIllustrationRelationRole.objects.all(),
		widget=PersonIllustrationRelationRoleWidget(**dselect2))

	class Meta:
		model = PersonIllustrationRelation
		fields = 'person,illustration,role'
		fields = fields.split(',')

personillustration_formset = inlineformset_factory(
	Person,PersonIllustrationRelation,
	form = PersonIllustrationRelationForm, extra=1)
illustrationperson_formset = inlineformset_factory(
	Illustration,PersonIllustrationRelation,
	form = PersonIllustrationRelationForm, extra=1)


class PersonLocationRelationForm(ModelForm):
	'''Form to add a person location relation'''
	location = forms.ModelChoiceField(
		queryset=Location.objects.all().order_by('name'),
		widget=LocationWidget(**dselect2n2))
	relation = forms.ModelChoiceField(
		queryset=PersonLocationRelationType.objects.all(),
		widget=PersonLocationRelationTypeWidget(**dselect2))
	start_year= forms.IntegerField(widget=forms.NumberInput(**dattr),required=False)
	end_year= forms.IntegerField(widget=forms.NumberInput(**dattr),required=False)

	class Meta:
		model = PersonLocationRelation
		fields = 'location,relation,start_year,end_year'
		fields = fields.split(',')

location_formset = inlineformset_factory(
	Person,PersonLocationRelation,
	form = PersonLocationRelationForm, extra=1)


class PersonPeriodicalRelationForm(ModelForm):
	'''Form to add a relation between a person and a periodical.'''
	person = forms.ModelChoiceField(
		queryset=Person.objects.all(),
		widget=PersonWidget(**dselect2))
	periodical = forms.ModelChoiceField(
		queryset=Periodical.objects.all().order_by('title'),
		widget=PeriodicalWidget(**dselect2))
	role = forms.ModelChoiceField(
		queryset=PersonPeriodicalRelationRole.objects.all(),
		widget=PersonPeriodicalRelationRoleWidget(**dselect2))

	class Meta:
		model = PersonPeriodicalRelation
		fields = ['person','periodical','role']

personperiodical_formset = inlineformset_factory(
	Person,PersonPeriodicalRelation,
	form = PersonPeriodicalRelationForm, extra=1)
periodicalperson_formset = inlineformset_factory(
	Periodical,PersonPeriodicalRelation,
	form = PersonPeriodicalRelationForm, extra=1)



