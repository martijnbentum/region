from .models import Person, LocationRelation, Pseudonym
from .models import PersonIllustrationRelationRole, PersonTextRelationRole
from .models import PersonMovementRelationRole,Movement, MovementType
from .models import PersonPersonRelationType
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget

#all select2 widgets related to person models are defined here
#select2 handles type searching for model instances
#use of these widgets enables delayed loading of the options (without this
# approach all instances of a model would be coded in the html, now it is send via
# ajax calls with json)

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


class PersonMovementRelationRoleWidget(ModelSelect2Widget):
	model = PersonMovementRelationRole
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return PersonMovementRelationRole.objects.all().order_by('name')

class MovementWidget(ModelSelect2Widget):
	model = Movement
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return Movement.objects.all().order_by('name')


class MovementTypeWidget(ModelSelect2Widget):
	model = MovementType
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return MovementType.objects.all().order_by('name')

class PersonPersonRelationTypeWidget(ModelSelect2Widget):
	model = PersonPersonRelationType
	search_fields = ['name__icontains']
	def label_from_instance(self,obj):
		return obj.name
	def get_queryset(self):
		return PersonPersonRelationType.objects.all().order_by('name')
