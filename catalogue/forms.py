from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.template.loader import render_to_string
from .models import Genre, Text, Publisher, Publication, Illustration, Periodical
from .models import IllustrationCategory, IllustrationPublicationRelation
from .models import TextPublicationRelation, TextTextRelation,PublicationType
from .models import TextTextRelationType, PeriodicalPublicationRelation
from .models import CopyRight, TextType, TextReviewPublicationRelation
from locations.models import UserLoc
from persons.models import Person, PersonLocationRelation, PersonTextRelation
from persons.models import PersonTextRelationRole, PersonIllustrationRelation
from persons.models import PersonIllustrationRelationRole 
from persons.widgets import PersonTextRelationRoleWidget, PersonWidget 
from persons.widgets import PersonIllustrationRelationRoleWidget
from utilities.models import Language 
from utilities.forms import LanguageWidget 
from locations.widgets import LocationWidget, LocationsWidget
from .widgets import GenreWidget, PublicationTypeWidget, PublishersWidget 
from .widgets import IllustrationCategoryWidget,IllustrationWidget,TextWidget
from .widgets import IllustrationCategoriesWidget,CopyRightWidget
from .widgets import TextTextRelationTypeWidget, PublicationWidget, PeriodicalWidget
from .widgets import TextTypeWidget


def make_select2_attr(field_name,input_length=2):
	attr= {'attrs':{'data-placeholder':'Select by '+field_name+' ...',
	'style':'width:100%','class':'searching','data-minimum-input-length':str(input_length)}}
	return attr
		

class PeriodicalPublicationRelationForm(ModelForm):
	'''Form to add a periodical publication relation'''
	publication = forms.ModelChoiceField(
		queryset=Publication.objects.all(),
		widget=PublicationWidget(
			attrs={'data-placeholder':'Select publication by title...',
			'style':'width:100%;','class':'searching'}))
	periodical= forms.ModelChoiceField(
		queryset=Periodical.objects.all(),
		widget=PeriodicalWidget(
			attrs={'data-placeholder':'Select periodical by title...',
			'style':'width:100%;','class':'searching'}))

	class Meta:
		model = PeriodicalPublicationRelation
		fields = 'publication,periodical,volume,issue'
		fields = fields.split(',')

#fromsets are symmetrically defined to be able to add the relation from both sides
publicationperiodical_formset = inlineformset_factory(
	Publication,PeriodicalPublicationRelation,
	form = PeriodicalPublicationRelationForm, extra=1)
periodicalpublication_formset = inlineformset_factory(
	Periodical,PeriodicalPublicationRelation,
	form = PeriodicalPublicationRelationForm, extra=1)


class IllustrationPublicationRelationForm(ModelForm):
	'''Form to add a illustration publication relation'''
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

#fromsets are symmetrically defined to be able to add the relation from both sides
publicationillustration_formset = inlineformset_factory(
	Publication,IllustrationPublicationRelation,
	form = IllustrationPublicationRelationForm, extra=1)
illustrationpublication_formset = inlineformset_factory(
	Illustration,IllustrationPublicationRelation,
	form = IllustrationPublicationRelationForm, extra=1)

class TextPublicationRelationForm(ModelForm):
	'''Form to add a text publication relation'''
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

#fromsets are symmetrically defined to be able to add the relation from both sides
publicationtext_formset = inlineformset_factory(
	Publication,TextPublicationRelation,
	form = TextPublicationRelationForm, extra=1)
textpublication_formset = inlineformset_factory(
	Text,TextPublicationRelation,
	form = TextPublicationRelationForm, extra=1)

class TextReviewPublicationRelationForm(ModelForm):
	'''Form to add a text publication relation'''
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
		model = TextReviewPublicationRelation
		fields = 'publication,text'
		fields = fields.split(',')

publicationreviewedbytext_formset = inlineformset_factory(
	Publication,TextReviewPublicationRelation,
	form = TextReviewPublicationRelationForm, extra=1)
textreviewpublication_formset = inlineformset_factory(
	Text,TextReviewPublicationRelation,
	form = TextReviewPublicationRelationForm, extra=1)


class TextTextRelationForm(ModelForm):
	'''Form to add a text relation.
	the relation is directional however on the front end we show it as if it is symmetrical
	review/reviewed translation/translated is not symmetrical but non trivial to implement'''
	primary = forms.ModelChoiceField(
		queryset=Text.objects.all(),
		widget=TextWidget(
			attrs={'data-placeholder':'Select text by title...',
			'style':'width:100%;','class':'searching'}))
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

#fromsets are symmetrically defined to be able to add the relation from both sides
#for relations between the same model the relation is asymmetrical
texttext_formset = inlineformset_factory(
	Text,TextTextRelation,fk_name = 'primary',
	form = TextTextRelationForm, extra=1)
texttextr_formset = inlineformset_factory(
	Text,TextTextRelation,fk_name = 'secondary',
	form = TextTextRelationForm, extra=0)

class TextTextRelationTypeForm(ModelForm):
	'''Form to add a textrelationtype e.g. translation'''
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
	'''Form to add a publication type e.g. novel'''
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
	text_type= forms.ModelChoiceField(
		queryset=TextType.objects.all().order_by('name'),
		widget=TextTypeWidget(**make_select2_attr('name',0)),
		required = False
		)
	title = forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	location= forms.ModelMultipleChoiceField(
		queryset=UserLoc.objects.all().order_by('name'),
		widget=LocationsWidget(attrs={'data-placeholder':'Select location(s)...',
			'style':'width:100%;','class':'searching'}),
		# widget=HeavySelect2Widget(data_view = 'catalogue:heavy_data'),
		required = False
		)
	setting= forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}),
		required=False)
	notes = forms.CharField(widget=forms.Textarea(
		attrs={'style':'width:100%','rows':3}),
		required=False)
	copyright= forms.ModelChoiceField(
		queryset=CopyRight.objects.all().order_by('name'),
		widget=CopyRightWidget(
			attrs={'data-placeholder':'Select licence...',
			'style':'width:100%;','class':'searching',
			'data-minimum-input-length':'0'}),
		required = False
		)
	source_link= forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}),
		required = False)


	class Meta:
		model = Text
		m = 'title,setting,language,genre,notes,location,complete,approved'
		m += ',copyright,source_link,text_type'
		fields = m.split(',')


class PublicationForm(ModelForm):
	'''Form to add a publication'''
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
	date = forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	copyright= forms.ModelChoiceField(
		queryset=CopyRight.objects.all().order_by('name'),
		widget=CopyRightWidget(
			attrs={'data-placeholder':'Select licence...',
			'style':'width:100%;','class':'searching',
			'data-minimum-input-length':'0'}),
		required = False
		)
	source_link= forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}),
		required = False)

		
	class Meta:
		model = Publication
		m = 'title,form,publisher,year,date,location,notes,pdf,cover,complete'
		m += ',approved,volume,issue,copyright,source_link'
		fields = m.split(',')


class PublisherForm(ModelForm):
	'''form to add publisher.'''
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
		m = 'name,location,founded,closure,notes,complete,approved'
		fields = m.split(',')


class GenreForm(ModelForm):
	'''form to add an illustration category.'''
	name = forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))

	class Meta:
		model = Genre
		fields = ['name']

class TextTypeForm(ModelForm):
	'''form to add an illustration category.'''
	name = forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))

	class Meta:
		model = TextType 
		fields = ['name']

class CopyRightForm(ModelForm):
	'''form to add an illustration category.'''
	name = forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))

	class Meta:
		model = CopyRight
		fields = ['name']

class IllustrationCategoryForm(ModelForm):
	'''form to add an illustration category.'''
	name = forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	notes = forms.CharField(widget=forms.Textarea(
		attrs={'style':'width:100%','rows':3}),
		required=False)

	class Meta:
		model = IllustrationCategory
		fields = 'name,notes'.split(',')
	

class IllustrationForm(ModelForm):
	'''Form to add an illustration.'''
	caption = forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	categories = forms.ModelMultipleChoiceField(
		queryset=IllustrationCategory.objects.all().order_by('name'),
		widget=IllustrationCategoriesWidget(
			attrs={'data-placeholder':'Select categories...',
			'style':'width:100%;','class':'searching',
			'data-minimum-input-length':'0'}),
		required = False
		)
	copyright= forms.ModelChoiceField(
		queryset=CopyRight.objects.all().order_by('name'),
		widget=CopyRightWidget(
			attrs={'data-placeholder':'Select licence...',
			'style':'width:100%;','class':'searching',
			'data-minimum-input-length':'0'}),
		required = False
		)
	source_link= forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}),
		required = False)
	page_number= forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}),
		required=False)
	notes = forms.CharField(widget=forms.Textarea(
		attrs={'style':'width:100%','rows':3}),
		required=False)

	class Meta:
		model = Illustration
		fields = 'caption,categories,page_number,notes,upload,complete,approved'
		fields += ',copyright,source_link'
		fields = fields.split(',')

class PeriodicalForm(ModelForm):
	'''Form to add an periodical.'''
	title= forms.CharField(widget=forms.TextInput(
		attrs={'style':'width:100%'}))
	founded= forms.IntegerField(widget=forms.NumberInput(
		attrs={'style':'width:100%'}),
		required=False)
	closure= forms.IntegerField(widget=forms.NumberInput(
		attrs={'style':'width:100%'}),
		required=False)
	location= forms.ModelMultipleChoiceField(
		queryset=UserLoc.objects.all().order_by('name'),
		widget=LocationsWidget(attrs={'data-placeholder':'Select location(s)...',
			'style':'width:100%;','class':'searching'}),
		# widget=HeavySelect2Widget(data_view = 'catalogue:heavy_data'),
		required = False
		)

	class Meta:
		model = Periodical
		fields = 'title,founded,closure,location,complete,approved'.split(',')



