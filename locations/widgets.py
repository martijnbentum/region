from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget
from .models import UserLoc, GeoLoc

class LocationWidget(ModelSelect2Widget):
	model = UserLoc 
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		if obj.country != '':
			m = obj.name + ' | ' + obj.country
			if obj.region != '':
				m += ' | ' +obj.region
		else: m = obj.name
		return m

	def get_queryset(self):
		return UserLoc.objects.all().order_by('name')


class LocationsWidget(ModelSelect2MultipleWidget):
	model = UserLoc 
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		if obj.country != '':
			m = obj.name + ' | ' + obj.country
			if obj.region != '':
				m += ' | ' + obj.region
		else: m = obj.name
		return m

	def get_queryset(self):
		return UserLoc.objects.all().order_by('name')


class GeoLocationWidget(ModelSelect2Widget):
	model = GeoLoc 
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		if obj.country != '':
			m = obj.name + ' | ' + obj.country
			if obj.region != '':
				m += ' | ' + obj.region
		else: m = obj.name
		return m

	def get_queryset(self):
		return GeoLoc.objects.all().order_by('name')

class GeoLocationsWidget(ModelSelect2MultipleWidget):
	model = GeoLoc 
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		if obj.country != '':
			m = obj.name + ' | ' + obj.country
			if obj.region != '':
				m += ' | ' +obj.region
		else: m = obj.name
		return m

	def get_queryset(self):
		return GeoLoc.objects.all().order_by('name')


class CountryWidget(ModelSelect2Widget):
	model = GeoLoc 
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		return obj.name 

	def get_queryset(self):
		return GeoLoc.objects.filter(location_type='COUNTRY').order_by('name')
