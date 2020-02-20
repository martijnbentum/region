from django import forms
from django.forms import ModelForm, inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset
from django_select2.forms import ModelSelect2Widget
from .models import Language


class LanguageWidget(ModelSelect2Widget):
	model = Language
	search_fields = ['name__startswith']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return Language.objects.all().order_by('name')


