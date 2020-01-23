from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.template.loader import render_to_string
from .models import Text
from django_select2.forms import Select2Widget,HeavySelect2Widget,ModelSelect2Widget
import json
from locations.models import UserLoc
from persons.models import Person, PersonLocationRelation
from utilities.models import Date, Language 
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, ButtonHolder, Submit



class TextForm(ModelForm):
	'''Form to add a text'''
	language = forms.ModelMultipleChoiceField(
		queryset=Language.objects.order_by('name'),
		widget=Select2Widget,
		required = False
		)

	class Meta:
		model = Text
		m = 'title,language,genre,upload,notes'
		fields = m.split(',')





