from django.apps import apps
from locations.models import UserLoc,GeoLoc,Location
from .hloc_util import make_locationtype, make_locationstatus, make_locationprecision
from locations.models import Location, LocationType, LocationStatus, LocationPrecision
from locations.models import LocationRelation 
from utilities.models import instance2names

def make():
	make_locationtype()
	make_locationstatus()
	make_locationprecision()

def userloc2Location(ul):
	gls = ul.geoloc_set.all()
	

def geoloc2location(gl, save = False):
	names = 'name,geonameid,coordinates_polygon,latitude,longitude,information'.split(',')
	kw = dict([[n,getattr(gl,n)] for n in names])
	l = Location(**kw)
	l.location_type = LocationType.objects.get(name=gl.location_type.lower())
	l.location_status= LocationStatus.objects.get(name='non-fiction')
	l.location_precision= LocationPrecision.objects.get(name='exact')
	ul = gl.user_locs.all()
	l.active = True if ul.count() > 0 else False
	if save: l.save()
	return l


def _handle_ul(ul,fd,field_name):
	location_type = ul.loc_type.name
	location_precision = ul.loc_precision
	location_status = ul.status
	geonameids = '|'.join([gl.geonameid for gl in ul.geoloc_set.all()])
	n = str(len(geonameids.split('|')))
	information = [location_type,location_precision,location_status,geonameids,n]
	if field_name not in fd.keys(): fd[field_name] = []
	fd[field_name].append(information)
	return fd

def _get_fields(instance):
	m2m = [[field,'m2m'] for field in instance._meta.__dict__['local_many_to_many']]
	fk = [[field,'fk'] for field in instance._meta.fields]
	return fk + m2m

def instance2userloc_information(instance):
	app_name, model_name = instance2names(instance)
	fields = _get_fields(instance)
	fd = {}
	for field,field_type in fields:
		print(field.name,field_type)
		try:related_model= str(field.remote_field.model).split(".")[-1].split("'")[0]
		except:related_model = False
		if related_model != 'UserLoc': continue
		ul = getattr(instance,field.name) 
		if field_type == 'fk' and ul: fd = _handle_ul(ul,fd,field.name)
		elif field_type == 'm2m' and ul:
			for x in ul.all():
				fd = _handle_ul(x,fd,field.name)
	return fd


def model2userloc_information(app_name,model_name):
	model = apps.get_model(app_name,model_name)
	model_dict = {}
	for instance in model.objects.all():
		fd = instance2userloc_information(instance)
		if fd != {}:
			model_dict[','.join([app_name,model_name,str(instance.pk)])]= fd
	return model_dict

def get_all_userloc_information():
	names = 'Text,Publication,Publisher,Illustration,Periodical'.split(',')
	names = [['catalogue',n] for n in names]
	names.extend( [['persons','Movement'],['persons','Person'],['persons','PersonLocationRelation']])
	od = {}
	for model in names:
		print(model)
		od.update(model2userloc_information(*model))
	return od
		





