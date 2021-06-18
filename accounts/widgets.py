from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget
from django.contrib.auth import get_user_model

User = get_user_model()

class UserWidget(ModelSelect2Widget):
	model = User
	search_fields = ['username__icontains']
	def label_from_instance(self,obj):
		return obj.username
	def get_queryset(self):
		return User.objects.all().order_by('username')
