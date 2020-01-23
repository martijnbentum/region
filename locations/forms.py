from django_select2.forms import ModelSelect2Widget
from .models import UserLoc

class LocationWidget(ModelSelect2Widget):
	model = UserLoc 
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return UserLoc.objects.all().order_by('name')
