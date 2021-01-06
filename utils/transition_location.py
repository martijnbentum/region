from django.apps import apps
from locations.models import UserLoc,GeoLoc,Location
from .hloc_util import make_locationtype, make_locationstatus, make_locationprecision
from locations.models import Location, LocationType, LocationStatus, LocationPrecision
from locations.models import LocationRelation 
from .model_util import instance2names

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

def _fix_precision(precision):
	dprecision = {'E':'exact','A':'approximate','R':'rough'}
	if precision in dprecision.keys():return dprecision[precision]
	return precision

def _fix_status(status):
	dstatus = {'F':'fiction','NF':'non-fiction'}
	if status in dstatus.keys():return dstatus[status]
	return status


def _handle_ul(ul,fd,field_name):
	location_type = ul.loc_type.name
	location_precision = _fix_precision(ul.loc_precision)
	location_status = _fix_status(ul.status)
	geonameids = '|'.join([gl.geonameid for gl in ul.geoloc_set.all()])
	n = str(len(geonameids.split('|')))
	information = [location_type,location_precision,location_status,geonameids,str(ul.pk),ul.name,n]
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
		
def get_instance(app_name,model_name,pk):
	model = apps.get_model(app_name,model_name)
	return model.objects.get(pk = pk)

def _set_related_instances(l,location_type,location_precision,location_status):
	l.location_type = LocationType.objects.get(name = location_type)
	l.location_precision= LocationPrecision.objects.get(name=location_precision)
	l.location_status= LocationStatus.objects.get(name = location_status)
	l.save()
	return l

def _get_locations(ul_info):
	geonameids = ul_info[3].split('|')
	print(geonameids,ul_info)
	if geonameids == ['']:
		locations = [_set_related_instances(Location(name= ul_info[-2]),*ul_info[:3]) ]
	else: locations = [Location.objects.get(geonameid=geonameid) for geonameid in geonameids]
	return locations


def _set_location(instance,field,locations,key,ul_info,clear =False):
	hloc_field = getattr(instance,'h'+field)
	if hasattr(hloc_field,'add'): hloc_field.clear()
	for location in locations:
		print(hloc_field,type(hloc_field))
		if hasattr(hloc_field,'add'):
			hloc_field.add(location)
		elif field == 'location': 
			instance.hlocation = location
		elif field == 'birth_place': 
			instance.hbirth_place= location
		elif field == 'death_place': 
			instance.hdeath_place= location
		else: not_handled.append([key,ul_info])
		print(key,field,ul_info,'handling location:',location,'ul name:',ul_info[-2])

def add_hlocation(key,value,not_handled):
	print(key)
	instance = get_instance(*key.split(','))
	for field in value.keys():
		for ul_info in value[field]:
			if ul_info[1] != 'exact' or ul_info[2] != 'non-fiction':
				print(key,field,ul_info,'not handled')
				not_handled.append([key,ul_info,field])
				continue
			locations = _get_locations(ul_info)
			_set_location(instance,field,locations,key,ul_info)
		print('---')
	instance.save()
		
		
def add_all_hlocations():
	all_userloc_information = get_all_userloc_information()
	not_handled = []
	for key, value in all_userloc_information.items():
		add_hlocation(key,value,not_handled)
	return not_handled, all_userloc_information
	
	
def handle_not_handled(nh):
	userlocs = []
	locs = []
	pks = []
	for line in nh:
		key,ul_info,field = line
		pk = int(ul_info[-3])
		instance = get_instance(*key.split(','))
		if pk not in pks:
			pks.append(pk)
			ul =UserLoc.objects.get(pk=pk)
			print(ul)
			try: l = Location.objects.get(geonameid = ul.name)
			except:
				l = Location(name = ul.name,geonameid = ul.name)
				l.location_type= LocationType.objects.get(name= ul.loc_type.name)
				l.location_precision= LocationPrecision.objects.get(name= ul.loc_precision)
				l.location_status = LocationStatus.objects.get(name=ul.status)
				l.active = True
				l.save()
				print('made',l)
			else: print(l,'already made')
			for geonameid in ul_info[3].split('|'):
				print('geonameid',geonameid)
				if not geonameid: continue
				rl = Location.objects.get(geonameid = geonameid)
				if rl.pk == l.pk: continue
				print('adding location:',rl)
				l.relations.add(rl)
			userlocs.append(ul)
			locs.append(l)
			print('---')
		locations = [Location.objects.get(geonameid = ul_info[-2])]
		_set_location(instance,field,locations,key,ul_info)
	return (userlocs,locs)

def check_all_hlocation(userloc_information= None):
	if userloc_information == None: userloc_information = get_all_userloc_information()
	total,ok_count,bad = 0,0,0
	bad_instances = []
	deleted = [] 
	for key, value in userloc_information.items():
		try:instance = get_instance(*key.split(','))
		except:deleted.append([key,value])
		for field in value.keys():
			total +=1
			try:f,fh = getattr(instance,field), getattr(instance,'h'+field)
			except:
				print(instance,field)
				break
			if hasattr(f,'add'):
				ok = True
				fall,fhall = f.all(),fh.all()
				falln, fhalln = [l.name for l in fall], [l.name for l in fhall]
				if len(falln) != len(fhalln): ok = False
				else:
					for word in falln:
						if word not in fhalln: ok = False
				if not ok:
					print(instance,'\n***\n',fall,'\n***\n',fhall)
					print('-'*50)
					bad +=1
					bad_instances.append(instance)
				else: ok_count += 1
			else:
				if not hasattr(fh,'name'):pass 
				elif f.name==fh.name: 
					ok_count += 1
					continue
				bad +=1
				bad_instances.append(instance)
				print(instance,'\n***\n',f,'\n***\n',fh)
				print('-'*50)
	print(total,ok_count,bad)
	return userloc_information, bad_instances, deleted
			
	




