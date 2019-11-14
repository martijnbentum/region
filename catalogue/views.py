from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from .models import Person

class PersonView(generic.ListView):
	template_name = 'catalogue/index.html'
	context_object_name = 'person_list'

	def get_queryset(self):
		return Person.objects.order_by('last_name')

# Create your views here.
