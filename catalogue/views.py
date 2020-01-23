from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
from utilities.models import Date
from persons.models import Person, PersonLocationRelation
from .models import Text
from .forms import TextForm 
import json
from locations.models import UserLoc


class TextView(generic.ListView):
	template_name = 'catalogue/text_list.html'
	context_object_name = 'text_list'

	def get_queryset(self):
		return Text.objects.order_by('title')


def add_text(request):
	# if this is a post request we need to process the form data
	if request.method == 'POST':
		form = PersonForm(request.POST)
		if form.is_valid():
			print('form is valid: ',form.cleaned_data,type(form))
			form.save()
			return HttpResponseRedirect('/text/')
	else:
		form = TextForm()
	var = {'form':form,'page_name':'Add text'}
	return render(request, 'catalogue/add_text.html', var)

# Create your views here.
