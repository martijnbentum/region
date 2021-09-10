from .models import Modelname
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget


class ModelnameWidget(ModelSelect2Widget):
	model = Modelname
	search_fields = ['model_name__icontains']

	def label_from_instance(self,obj):
		return obj.model_name

	def get_queryset(self):
		return Modelname.objects.all().order_by('model_name')
