from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget
from .models import Location, LocationType, LocationStatus,LocationPrecision

class LocationTypeWidget(ModelSelect2Widget):
	model = LocationType
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return LocationType.objects.all().order_by('name')

class LocationStatusWidget(ModelSelect2Widget):
	model = LocationStatus
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return LocationStatus.objects.all().order_by('name')

class LocationPrecisionWidget(ModelSelect2Widget):
	model = LocationPrecision
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return LocationPrecision.objects.all().order_by('name')


class LocationWidget(ModelSelect2Widget):
	model = Location
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		if obj.country != '':
			m = obj.name
			if obj.region != '':
				m += ' | ' + obj.region
			m += ' | ' + obj.country
		else: m = obj.name + obj.gps
		return m

	def get_queryset(self):
		return Location.objects.all().order_by('name')

class LocationsWidget(ModelSelect2MultipleWidget):
	model = Location
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		if obj.country != '':
			m = obj.name + ' | ' + obj.country
			if obj.region != '':
				m += ' | ' +obj.region
		else: m = obj.name + ' | ' + obj.gps
		
		return m

	def get_queryset(self):
		return Location.objects.all().order_by('name')


class LocationVerboseWidget(ModelSelect2Widget):
	model = Location
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		return obj.name + ' | ' + obj.location_type.name

	def get_queryset(self):
		return Location.objects.all().order_by('name')
