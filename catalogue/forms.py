from django import forms
from django.forms import ModelForm, inlineformset_factory, modelform_factory
from .models import Genre, Text, Publisher, Publication, Illustration, Periodical
from .models import IllustrationCategory, IllustrationPublicationRelation
from .models import TextPublicationRelation, TextTextRelation,PublicationType
from .models import TextTextRelationType, PeriodicalPublicationRelation
from .models import CopyRight, TextType, TextReviewPublicationRelation, Item
from .models import IllustrationIllustrationRelation, IllustrationIllustrationRelationType
from .models import IllustrationType
from locations.models import Location
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
from .widgets import TextTypeWidget, IllustrationTypeWidget,IllustrationIllustrationRelationTypeWidget
from utilities.forms import make_select2_attr 

# setting default kwargs to clean up form definition

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
names = 'CopyRight,Genre,TextType,TextTextRelationType,IllustrationType'
names += ',PublicationType,IllustrationCategory,IllustrationIllustrationRelationType'
names = names.split(',')
for name in names:
	create_simple_form(name)


item_fields = 'description,notes,complete,approved,source_link,copyright'
item_fields = item_fields.split(',')

class ItemForm(ModelForm):
	'''base form for main catalogue models.'''
	description =forms.CharField(**dtext)
	notes =forms.CharField(**dtext)
	source_link= forms.CharField(**dchar)
	copyright = forms.ModelChoiceField(
		queryset=CopyRight.objects.all(),
		widget=CopyRightWidget(**dselect2),
		required=False)

	class Meta:
		model =Item
		fields=item_fields


class PublicationForm(ItemForm):
	'''Form to add a publication'''
	form = forms.ModelChoiceField(
		queryset=PublicationType.objects.all().order_by('name'),
		widget=PublicationTypeWidget(
			attrs={'data-placeholder':'Select publication form... e.g., novel',
			'style':'width:100%;','class':'searching',
			'data-minimum-input-length':'0'}),
		required = False)
	publisher = forms.ModelMultipleChoiceField(
		queryset=Publisher.objects.all().order_by('name'),
		widget=PublishersWidget(**dselect2),
		required=False)
	location= forms.ModelMultipleChoiceField(
		queryset=Location.objects.all().order_by('name'),
		widget=LocationsWidget(**dselect2n2),
		required = False)
	title = forms.CharField(**dchar_required)
	date = forms.CharField(**dchar_required)
		
	class Meta:
		model = Publication
		m = 'title,form,publisher,date,location,pdf,cover'
		m += ',volume,issue,publisher_names'
		fields = item_fields + m.split(',')


class PublisherForm(ItemForm):
	'''form to add publisher.'''
	location= forms.ModelMultipleChoiceField(
		queryset=Location.objects.all().order_by('name'),
		widget=LocationsWidget(**dselect2n2),
		required = False)
	name = forms.CharField(**dchar_required)
	founded = forms.IntegerField(widget=forms.NumberInput(**dattr),required=False)
	closure = forms.IntegerField(widget=forms.NumberInput(**dattr),required=False)

	class Meta:
		model = Publisher
		m = 'name,location,founded,closure'
		fields = item_fields + m.split(',')
		

class TextForm(ItemForm):
	'''Form to add a text'''
	language = forms.ModelChoiceField(
		queryset=Language.objects.all().order_by('name'),
		widget=LanguageWidget(**dselect2),
		required = False)
	genre = forms.ModelChoiceField(
		queryset=Genre.objects.all().order_by('name'),
		widget=GenreWidget(**dselect2),
		required = False)
	text_type= forms.ModelChoiceField(
		queryset=TextType.objects.all().order_by('name'),
		widget=TextTypeWidget(**dselect2),
		required = False)
	title = forms.CharField(**dchar_required)
	location= forms.ModelMultipleChoiceField(
		queryset=Location.objects.all().order_by('name'),
		widget=LocationsWidget(**dselect2n2),
		required = False)
	setting= forms.CharField(**dchar)

	class Meta:
		model = Text
		m = 'title,setting,language,genre,location'
		m += ',text_type'
		fields = item_fields + m.split(',')


class IllustrationForm(ItemForm):
	'''Form to add an illustration.'''
	caption = forms.CharField(**dchar_required)
	categories = forms.ModelMultipleChoiceField(
		queryset=IllustrationCategory.objects.all().order_by('name'),
		widget=IllustrationCategoriesWidget(**dselect2),
		required = False)
	page_number= forms.CharField(**dchar)
	Illustration_type= forms.ModelChoiceField(
		queryset=TextType.objects.all().order_by('name'),
		widget=IllustrationTypeWidget(**dselect2),
		required = False)
	illustration_type= forms.ModelChoiceField(
		queryset=IllustrationType.objects.all().order_by('name'),
		widget=IllustrationTypeWidget(**dselect2),
		required = False)

	class Meta:
		model = Illustration
		fields = 'caption,categories,page_number,upload,illustration_type,image_filename'
		fields = item_fields + fields.split(',')


class PeriodicalForm(ItemForm):
	'''Form to add an periodical.'''
	title= forms.CharField(**dchar_required)
	founded= forms.IntegerField(widget=forms.NumberInput(**dattr),required=False)
	closure= forms.IntegerField(widget=forms.NumberInput(**dattr),required=False)
	location= forms.ModelMultipleChoiceField(
		queryset=Location.objects.all().order_by('name'),
		widget=LocationsWidget(**dselect2n2),
		required = False)

	class Meta:
		model = Periodical
		fields = item_fields + 'title,founded,closure,location'.split(',')




# --- relational forms ---

class PeriodicalPublicationRelationForm(ModelForm):
	'''Form to add a periodical publication relation'''
	publication = forms.ModelChoiceField(
		queryset=Publication.objects.all(),
		widget=PublicationWidget(**dselect2))
	periodical= forms.ModelChoiceField(
		queryset=Periodical.objects.all(),
		widget=PeriodicalWidget(**dselect2))

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
		widget=PublicationWidget(**dselect2))
	illustration = forms.ModelChoiceField(
		queryset=Illustration.objects.all(),
		widget=IllustrationWidget(**dselect2))

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
		widget=PublicationWidget(**dselect2))
	text = forms.ModelChoiceField(
		queryset=Text.objects.all(),
		widget=TextWidget(**dselect2))

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
		widget=PublicationWidget(**dselect2))
	text = forms.ModelChoiceField(
		queryset=Text.objects.all(),
		widget=TextWidget(**dselect2))

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
		widget=TextWidget(**dselect2))
	secondary = forms.ModelChoiceField(
		queryset=Text.objects.all(),
		widget=TextWidget(**dselect2))
	relation_type = forms.ModelChoiceField(
		queryset=TextTextRelationType.objects.all(),
		widget=TextTextRelationTypeWidget(**dselect2))

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


class IllustrationIllustrationRelationForm(ModelForm):
	'''Form to add a illustration relation.
	the relation is directional however on the front end we show it as if it is symmetrical
	review/reviewed translation/translated is not symmetrical but non trivial to implement'''
	primary = forms.ModelChoiceField(
		queryset=Illustration.objects.all(),
		widget=IllustrationWidget(**dselect2))
	secondary = forms.ModelChoiceField(
		queryset=Illustration.objects.all(),
		widget=IllustrationWidget(**dselect2))
	relation_type = forms.ModelChoiceField(
		queryset=IllustrationIllustrationRelationType.objects.all(),
		widget=IllustrationIllustrationRelationTypeWidget(**dselect2))

	class Meta:
		model = IllustrationIllustrationRelation
		fields = 'secondary,relation_type'
		fields = fields.split(',')

#fromsets are symmetrically defined to be able to add the relation from both sides
#for relations between the same model the relation is asymmetrical
illustrationillustration_formset= inlineformset_factory(
	Illustration,IllustrationIllustrationRelation,fk_name = 'primary',
	form = IllustrationIllustrationRelationForm, extra=1)
illustrationillustration_formsetr = inlineformset_factory(
	Illustration,IllustrationIllustrationRelation,fk_name = 'secondary',
	form = IllustrationIllustrationRelationForm, extra=0)



