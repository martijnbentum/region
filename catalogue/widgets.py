from .models import Text, Illustration, Genre, Publisher, PublicationType, Publication
from .models import Periodical, CopyRight, TextType
from .models import IllustrationCategory, TextTextRelationType
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget

#all select2 widgets related to catalogue models are defined here
#select2 handles type searching for model instances
#use of these widgets enables delayed loading of the options (without this
# approach all instances of a model would be coded in the html, now it is send via
# ajax calls with json)

class CopyRightWidget(ModelSelect2Widget):
	model = CopyRight
	search_fields = ['name__icontains']
	def label_from_instance(self,obj):
		return obj.name
	def get_queryset(self):
		return CopyRight.objects.all().order_by('name')


class TextTypeWidget(ModelSelect2Widget):
	model = TextType
	search_fields = ['name__icontains']
	def label_from_instance(self,obj):
		return obj.name
	def get_queryset(self):
		return TextType.objects.all().order_by('name')

class IllustrationCategoryWidget(ModelSelect2Widget):
	model = IllustrationCategory
	search_fields = ['name__icontains']
	def label_from_instance(self,obj):
		return obj.name
	def get_queryset(self):
		return IllustrationCategory.objects.all().order_by('name')

class IllustrationCategoriesWidget(ModelSelect2MultipleWidget):
	model = IllustrationCategory
	search_fields = ['name__icontains']
	def label_from_instance(self,obj):
		return obj.name
	def get_queryset(self):
		return IllustrationCategory.objects.all().order_by('name')

class GenreWidget(ModelSelect2Widget):
	model = Genre 
	search_fields = ['name__startswith']
	def label_from_instance(self,obj):
		return obj.name
	def get_queryset(self):
		return Genre.objects.all().order_by('name')


class IllustrationWidget(ModelSelect2Widget):
	model = Illustration
	search_fields = ['caption__icontains']
	def label_from_instance(self,obj):
		return obj.caption
	def get_queryset(self):
		return Illustration.objects.all().order_by('caption')


class PublisherWidget(ModelSelect2Widget):
	model = Publisher
	search_fields = ['name__icontains']
	def label_from_instance(self,obj):
		return obj.name
	def get_queryset(self):
		return Publisher.objects.all().order_by('name')


class PublishersWidget(ModelSelect2MultipleWidget):
	model = Publisher
	search_fields = ['name__icontains']
	def label_from_instance(self,obj):
		return obj.name
	def get_queryset(self):
		return Publisher.objects.all().order_by('name')


class TextWidget(ModelSelect2Widget):
	model = Text
	search_fields = ['title__icontains']
	def label_from_instance(self,obj):
		return obj.title
	def get_queryset(self):
		return Text.objects.all().order_by('title')


class PublicationTypeWidget(ModelSelect2Widget):
	model = PublicationType
	search_fields = ['name__icontains']
	def label_from_instance(self,obj):
		return obj.name
	def get_queryset(self):
		return PublicationType.objects.all().order_by('name')

class PublicationWidget(ModelSelect2Widget):
	model = Publication
	search_fields = ['title__icontains']
	def label_from_instance(self,obj):
		return obj.title
	def get_queryset(self):
		return Publication.objects.all().order_by('title')

class PeriodicalWidget(ModelSelect2Widget):
	model = Periodical
	search_fields = ['title__icontains']
	def label_from_instance(self,obj):
		return obj.title
	def get_queryset(self):
		return Periodical.objects.all().order_by('title')


class TextTextRelationTypeWidget(ModelSelect2Widget):
	model = TextTextRelationType
	search_fields = ['name__icontains']
	def label_from_instance(self,obj):
		return obj.name
	def get_queryset(self):
		return TextTextRelationType.objects.all().order_by('name')
