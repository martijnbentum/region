from .models import Person, LocationRelation, Pseudonym
from .models import PersonIllustrationRelationRole, PersonTextRelationRole
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget


class LocationRelationWidget(ModelSelect2Widget):
	model = LocationRelation 
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return LocationRelation.objects.all().order_by('name')


class PersonWidget(ModelSelect2Widget):
	model = Person
	search_fields = ['first_name__icontains','last_name__icontains']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return Person.objects.all().order_by('last_name')


class PersonIllustrationRelationRoleWidget(ModelSelect2Widget):
	model = PersonIllustrationRelationRole
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return PersonIllustrationRelationRole.objects.all()


class PersonTextRelationRoleWidget(ModelSelect2Widget):
	model = PersonTextRelationRole
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return PersonTextRelationRole.objects.all()


class PseudonymsWidget(ModelSelect2MultipleWidget):
	model = Pseudonym
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return Pseudonym.objects.all().order_by('name')
