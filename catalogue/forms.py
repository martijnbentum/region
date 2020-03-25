from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.template.loader import render_to_string
from .models import Genre, Text, Publisher, Publication, Illustration 
from .models import IllustrationCategory, IllustrationPublicationRelation
from .models import TextPublicationRelation, TextTextRelation,PublicationType
from .models import TextTextRelationType 
from locations.models import UserLoc
from persons.models import Person, PersonLocationRelation, PersonTextRelation
from persons.models import PersonTextRelationRole, PersonIllustrationRelation
from persons.models import PersonIllustrationRelationRole
from persons.widgets import PersonTextRelationRoleWidget, PersonWidget 
from persons.widgets import PersonIllustrationRelationRoleWidget
from utilities.models import Language 
from utilities.forms import LanguageWidget 
from locations.forms import LocationWidget, LocationsWidget
from .widgets import GenreWidget, PublicationTypeWidget, PublishersWidget 
from .widgets import IllustrationCategoryWidget,IllustrationWidget,TextWidget
from .widgets import TextTextRelationTypeWidget, PublicationWidget



class IllustrationPublicationRelationForm(ModelForm):
	'''Form to add a person location relation'''
	publication = forms.ModelChoiceField(
		queryset=Publication.objects.all(),
		widget=PublicationWidget(
			attrs={'data-placeholder':'Select publication by title...',
			'style':'width:100%;','class':'searching'}))
	illustration = forms.ModelChoiceField(
		queryset=Illustration.objects.all(),
		widget=IllustrationWidget(
			attrs={'data-placeholder':'Select illustration by title...',
			'style':'width:100%;','class':'searching'}))

	class Meta:
		model = IllustrationPublicationRelation
		fields = 'publication,illustration,page'
		fields = fields.split(',')

publicationillustration_formset = inlineformset_factory(
	Publication,IllustrationPublicationRelation,
	form = IllustrationPublicationRelationForm, extra=1)
illustrationpublication_formset = inlineformset_factory(
	Illustration,IllustrationPublicationRelation,
	form = IllustrationPublicationRelationForm, extra=1)

class TextPublicationRelationForm(ModelForm):
	'''Form to add a person location relation'''
	publication = forms.ModelChoiceField(
		queryset=Publication.objects.all(),
		widget=PublicationWidget(
			attrs={'data-placeholder':'Select publication by title...',
			'style':'width:100%;','class':'searching'}))
	text = forms.ModelChoiceField(
		queryset=Text.objects.all(),
		widget=TextWidget(
			attrs={'data-placeholder':'Select text by title...',
			'style':'width:100%;','class':'searching'}))

	class Meta:
		model = TextPublicationRelation
		fields = 'publication,text,start_page,end_page'
		fields = fields.split(',')

publicationtext_formset = inlineformset_factory(
	Publication,TextPublicationRelation,
	form = TextPublicationRelationForm, extra=1)
textpublication_formset = inlineformset_factory(
	Text,TextPublicationRelation,
	form = TextPublicationRelationForm, extra=1)


class TextTextRelationForm(ModelForm):
	'''Form to add a person location relation'''
	secondary = forms.ModelChoiceField(
		queryset=Text.objects.all(),
		widget=TextWidget(
			attrs={'data-placeholder':'Select text by title...',
			'style':'width:100%;','class':'searching'}))
	relation_type = forms.ModelChoiceField(
		queryset=TextTextRelationType.objects.all(),
		widget=TextTextRelationTypeWidget(
			attrs={'data-placeholder':'Select a relation...',
			'style':'width:100%;','class':'searching',
			'data-minimum-input-length':'0'}))

	class Meta:
		model = TextTextRelation
		fields = 'secondary,relation_type'
		fields = fields.split(',')

texttext_formset = inlineformset_factory(
	Text,TextTextRelation,fk_name = 'primary',
	form = TextTextRelationForm, extra=1)

class TextTextRelationTypeForm(ModelForm):
	'''Form to add a text'''
	name = forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	notes = forms.CharField(widget=forms.Textarea(
		attrs={'style':'width:100%','rows':3}),
		required=False)
		
	class Meta:
		model = TextTextRelationType
		m = 'name,notes'
		fields = m.split(',')

class PublicationTypeForm(ModelForm):
	'''Form to add a text'''
	name = forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	notes = forms.CharField(widget=forms.Textarea(
		attrs={'style':'width:100%','rows':3}),
		required=False)
		
	class Meta:
		model = PublicationType
		m = 'name,notes'
		fields = m.split(',')

class TextForm(ModelForm):
	'''Form to add a text'''
	language = forms.ModelChoiceField(
		queryset=Language.objects.all().order_by('name'),
		widget=LanguageWidget(attrs={'data-placeholder':'Select language...',
			'style':'width:100%;','class':'searching',
			'data-minimum-input-length':'0'}),
		required = False
		)
	genre = forms.ModelChoiceField(
		queryset=Genre.objects.all().order_by('name'),
		widget=GenreWidget(attrs={'data-placeholder':'Select genre...',
			'style':'width:100%;','class':'searching',
			'data-minimum-input-length':'0'}),
		required = False
		)
	title = forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	setting= forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}),
		required=False)
	notes = forms.CharField(widget=forms.Textarea(
		attrs={'style':'width:100%','rows':3}),
		required=False)

	class Meta:
		model = Text
		m = 'title,setting,language,genre,notes'
		fields = m.split(',')


class PublicationForm(ModelForm):
	'''Form to add a text'''
	form = forms.ModelChoiceField(
		queryset=PublicationType.objects.all().order_by('name'),
		widget=PublicationTypeWidget(
			attrs={'data-placeholder':'Select publication form... e.g., novel',
			'style':'width:100%;','class':'searching',
			'data-minimum-input-length':'0'}),
		required = False
		)
	publisher = forms.ModelMultipleChoiceField(
		queryset=Publisher.objects.all().order_by('name'),
		widget=PublishersWidget(attrs={'data-placeholder':'Select publisher(s)',
			'style':'width:100%;','class':'searching'}),
		required = False
		)
	location= forms.ModelMultipleChoiceField(
		queryset=UserLoc.objects.all().order_by('name'),
		widget=LocationsWidget(attrs={'data-placeholder':'Select location(s)...',
			'style':'width:100%;','class':'searching'}),
		required = False
		)
	title = forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	setting= forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}),
		required=False)
	notes = forms.CharField(widget=forms.Textarea(
		attrs={'style':'width:100%','rows':3}),
		required=False)
		
	class Meta:
		model = Publication
		m = 'title,form,publisher,year,location,notes,pdf,cover'
		fields = m.split(',')


class PublisherForm(ModelForm):
	'''Company that publishes works.'''
	location= forms.ModelMultipleChoiceField(
		queryset=UserLoc.objects.all().order_by('name'),
		widget=LocationsWidget(attrs={'data-placeholder':'Select location(s)...',
			'style':'width:100%;','class':'searching'}),
		# widget=HeavySelect2Widget(data_view = 'catalogue:heavy_data'),
		required = False
		)
	name = forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	founded = forms.IntegerField(widget=forms.NumberInput(
		attrs={'style':'width:100%'}),required=False)
	closure = forms.IntegerField(widget=forms.NumberInput(
		attrs={'style':'width:100%'}),required=False)
	notes = forms.CharField(widget=forms.Textarea(
		attrs={'style':'width:100%','rows':3}),
		required=False)

	class Meta:
		model = Publisher
		m = 'name,location,founded,closure,notes'
		fields = m.split(',')


class IllustrationCategoryForm(ModelForm):
	name = forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	notes = forms.CharField(widget=forms.Textarea(
		attrs={'style':'width:100%','rows':3}),
		required=False)

	class Meta:
		model = IllustrationCategory
		fields = 'name,notes'.split(',')
	

class IllustrationForm(ModelForm):
	caption = forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	category = forms.ModelChoiceField(
		queryset=IllustrationCategory.objects.all().order_by('name'),
		widget=IllustrationCategoryWidget(
			attrs={'data-placeholder':'Select category...',
			'style':'width:100%;','class':'searching',
			'data-minimum-input-length':'0'}),
		required = False
		)
	page_number= forms.IntegerField(widget=forms.NumberInput(
		attrs={'style':'width:100%'}),
		required=False)
	notes = forms.CharField(widget=forms.Textarea(
		attrs={'style':'width:100%','rows':3}),
		required=False)

	class Meta:
		model = Illustration
		fields = 'caption,category,page_number,notes,upload'.split(',')


