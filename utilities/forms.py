from django import forms
from django.forms import ModelForm, inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset

class DateForm(ModelForm):
	'''form to add a person'''

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = formhelper()
		self.helper.add_input(
			submit('submit', 'save', css_class='btn-success'))
		self.helper.form_method = 'post'

		self.helper.layout= layout(
			row(
				column('start', css_class='form-group col-md-6 mb-0'),
				column('end', css_class='form-group col-md-6 mb-0'),
				css_class='from-row'
			),
			'start_specificity',
			'end_specificity',
			)

	class Meta:
		model = Date
		fields = 'start,end,start_specificity,end_specificity'.split(',')
		attrs={'class':'form-control',
			'type':'date'}
		widgets = {
			'date_start': forms.DateInput(
				format=('%d %m $Y'),
				attrs= attrs
				),
			'date_end': forms.DateInput(
				format=('%d %m $Y'),
				attrs= attrs
				)
		}
		labels = {'start_spec':'start specificity',
			'end_spec':'end specificity'}
