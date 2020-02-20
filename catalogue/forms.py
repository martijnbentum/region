from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.template.loader import render_to_string
from .models import Genre, Text, Publisher, Publication,Type, Illustration 
from .models import IllustrationCategory
from django_select2.forms import Select2Widget,ModelSelect2MultipleWidget,HeavySelect2Widget,ModelSelect2Widget
from locations.models import UserLoc
from persons.models import Person, PersonLocationRelation
from utilities.models import Language 
from utilities.forms import LanguageWidget 
from locations.forms import LocationWidget, LocationsWidget
from .widgets import GenreWidget, TypeWidget, PublishersWidget 
from .widgets import IllustrationCategoryWidget 



class TypeForm(ModelForm):
	'''Form to add a text'''
	name = forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	notes = forms.CharField(widget=forms.Textarea(
		attrs={'style':'width:100%','rows':3}),
		required=False)
		
	class Meta:
		model = Type
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
		m = 'title,setting,language,genre,upload,notes'
		fields = m.split(',')


class PublicationForm(ModelForm):
	'''Form to add a text'''
	form = forms.ModelChoiceField(
		queryset=Type.objects.all().order_by('name'),
		widget=TypeWidget(
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
		m = 'title,form,publisher,year,location,notes,upload'
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
		attrs={'style':'width:100%'}))
	closure = forms.IntegerField(widget=forms.NumberInput(
		attrs={'style':'width:100%'}))
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


