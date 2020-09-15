from utilities.models import instance2name, instance2names
from locations.models import Location
import random
from utilities.models import instance2name, instance2color, instance2icon, instance2map_buttons

def instance2related_locations(instance):
	'''returns all locations from related instances (foreign keys and m2m) 
	assumes related models have location_field <str> that specifies the fields with
	locations.
	'''
	locations = []
	field_names = instance2related_fieldnames(instance)
	for field_name, field_type in field_names:
		#field type is either fk or m2m for foreign keys / many to many relations
		ls =[]
		related_instance= getattr(instance,field_name)
		if not related_instance: continue
		if field_type == 'fk':
			# skip related instance with no location fielf (contains string holding the name of the
			# location field)
			if not hasattr(related_instance,'location_field'): continue
			ls = field2locations(related_instance,related_instance.location_field)
			model_name = instance2name(related_instance)
			if ls: # if there are locations set on the related instance add them to the output
				ls =[[field_name.replace('_set',''),model_name,l,related_instance] for l in ls]
				locations.extend(ls)
		if field_type == 'm2m':
			# handle m2m related instances
			for rl in related_instance.all():
				#for each m2m multiple instance can be related
				if not hasattr(rl,'location_field'): continue
				model_name = instance2name(rl)
				ls=field2locations(rl,rl.location_field)
				if ls: # if there are locations set on the related instance add them to the output
					ls =[[field_name.replace('_set',''),model_name,l,rl] for l in ls]
					locations.extend(ls)
	return locations,field_names
	

def field2locations(instance, field_name):
	'''return locations from a field (fk or m2m) on a model.'''
	if not hasattr(instance,field_name):return None
	x = getattr(instance,field_name)
	if type(x) == Location: return [x]
	if 'ManyRelatedManager' in str(type(x)): 
		return list(x.all())
	print('field:',field_name,'on:',instance,'is of unknown type:',type(x))
	return None

		
	
def instance2related_fieldnames(instance):
	'''returns a list of lists with fields names that are either fk or m2m (with type in str)
	[<field>,<str>field_type]
	extends this list with reversed relations (fields ending in _set)
	'''
	fn = []
	for field in instance._meta.__dict__['local_fields']:
		if 'Foreign Key' in field.description:
			fn.append([field.name,'fk'])
	for field in instance._meta.__dict__['local_many_to_many']:
		fn.append([field.name,'m2m'])
	fn.extend([[name,'m2m'] for name in dir(instance) if name.endswith('_set')])
	return fn

def queryset2maplist(qs,roles = [],perturbe= False,combine =False):
	'''Create a list of lists with information to create leaflet popups from a queryset.'''
	o = []
	for i,instance in enumerate(qs):
		if not hasattr(instance,'latlng') or not instance.latlng: continue
		for latlng in instance.latlng:
			name = instance2name(instance).lower()
			popup = instance.pop_up
			markerid = name + str(instance.pk)
			if perturbe: latlng = perturbe_latlng(latlng)
			if roles:o.append([name,latlng,popup,markerid,roles[i].replace('_',' ')])
			else:o.append([name,latlng,popup,markerid])
	if combine:  o =combine_popups(o)
	return o

def combine_popups(o):
	'''Combines popup content of multiple instances into one popup content.'''
	no = []
	dublicate_locations = {}
	for line in o:
		if line[1] in dublicate_locations.keys(): dublicate_locations[line[1]].append(line)
		else: dublicate_locations[line[1]] = [line]
	for key, value in dublicate_locations.items():
		if len(value) > 1:
			popups = '<hr>'.join([x[2] for x in value])
			ids = ':'.join([x[3] for x in value])
			new_line = [value[0][0],key,popups,ids]
			no.append(new_line)
		else:
			no.append(value[0])
	return no

def perturbe_latlng(latlng):
	lat,lng = map(float,latlng.split(', '))
	lat+=(random.random() - 0.5) /50 
	lng+=(random.random() - 0.5) /50 
	return ','.join(map(str,[lat,lng]))

	
def pop_up(instance):
	app_name, model_name = instance2names(instance)
	m = ''
	if hasattr(instance,'thumbnail'):
		if instance.thumbnail.name:
			m += '<img src="'+self.thumbnail.url+'" width="200" style="broder-radius:3">'
	m += instance2icon(instance)
	m += '<p class="h6 mb-0 mt-1" style="color:'+instance2color(instance)+';">'
	m += instance.instance_name+'</p>'
	m += '<hr class="mt-1 mb-0" style="border:1px solid '+instance2color(instance)+';">'
	m += '<p class="mt-2 mb-0">'+instance.description+'</p>'

	if hasattr(instance,'play_field'):
		link =  getattr(instance,getattr(intance,'play_field'))
		if link:
			m += '<a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" target="_blank" href='
			m += link
			m += 'role="button"><i class="fas fa-play"></i></a>'
	m += instance2map_buttons(instance)
	return m
	

		
