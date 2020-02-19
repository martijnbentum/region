from .models import Text, Illustration, Genre, Publisher, Type
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget


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


class TypeWidget(ModelSelect2Widget):
	model = Type
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return Type.objects.all().order_by('name')
