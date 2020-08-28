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

def make_select2_attr(field_name = 'name', input_length = 2):
	attr= {'attrs':{'data-placeholder':'Select by '+field_name+' ...',
	'style':'width:100%','class':'searching','data-minimum-input-length':str(input_length)}} 
	return attr
