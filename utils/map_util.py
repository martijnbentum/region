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
	source_model_name = instance2name(instance).lower()
	map_list = []
	for field_name, field_type in field_names:
		#field type is either fk or m2m for foreign keys / many to many relations
		print(field_name)
		fn = field_name.replace('_set','')
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
				ls =[[fn,model_name,l,related_instance] for l in ls]
				locations.extend(ls)
				map_list.extend(instance2maprows(related_instance,role=fn))
		if field_type == 'm2m':
			# handle m2m related instances
			for rl in related_instance.all():
				#for each m2m multiple instance can be related
				if not hasattr(rl,'location_field'): continue
				model_name = instance2name(rl)
				ls=field2locations(rl,rl.location_field)
				if ls: # if there are locations set on the related instance add them to the output
					ls =[[fn,model_name,l,rl] for l in ls]
					locations.extend(ls)
					map_list.extend(instance2maprows(rl,role=fn))
		if field_type == 'relation':
			for rl in related_instance.all():
				name = rl.other(source_model_name)
				if name:
					x = getattr(rl,name)
					if not hasattr(x,'location_field'): continue
					ls = field2locations(x,x.location_field)
					if ls:
						ls =[[field_name.replace('_set',''),name,l,x] for l in ls]
						locations.extend(ls)
						print(ls,222)
						print(rl,field_name,333)
						print(instance2maprows(rl,field_name))
						role = rl.relationship if hasattr(rl,'relationship') else fn 
						map_list.extend(instance2maprows(x,role=role))
						print(ls,222)
		if field_type == 'locationrelation':
			for rl in related_instance.all():
				name = rl.other(source_model_name)
				if not name: continue
				l = getattr(rl,name)
				if not l: continue
				print(field_name,name,8,l)
				locations.append([field_name.replace('_set',''),source_model_name,l,instance])
				role = rl.relationship if rl.relationship else fn
				print(role,101010101)
				mr = instance2maprows(instance,latlng=l.latlng,pop_up=instance.pop_up,role=role)
				map_list.append(mr)
	return locations,field_names,map_list
	

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
	for name in dir(instance):
		if not name.endswith('_set'): continue
		related_instances= getattr(instance,name)
		if related_instances: ri = related_instances.all()
		print(ri,field.name)
		if ri and 'LocationRelation' in instance2name(ri[0]):
			fn.append([name,'locationrelation'])
		elif ri and 'Relation' in instance2name(ri[0]):
			fn.append([name,'relation'])
		else:fn.append([name,'m2m'])
	# fn.extend([[name,'m2m'] for name in dir(instance) if name.endswith('_set')])
	return fn


def instance2maprows(instance,cull=True,pop_up = None,latlng=None,role = ''):
	if not hasattr(instance,'latlng') or not instance.latlng: return False
	o = []
	name = instance2name(instance).lower()
	markerid = name + str(instance.pk)
	print(role,123321)
	if pop_up == None:pop_up = instance.pop_up
	if latlng: return [name,latlng,pop_up,markerid,role]
	for i,latlng in enumerate(instance.latlng):
		if not role and hasattr(instance,'latlng_roles'):role = instance.latlng_roles[i]
		o.append([name,latlng,pop_up,markerid,role])
	if cull: o = cull_maplist(o)
	return o

def queryset2maplist(qs,combine =False, cull = True):
	'''Create a list of lists with information to create leaflet popups from a queryset.'''
	o = []
	for i,instance in enumerate(qs):
		map_rows= instance2maprows(instance,cull)
		if not map_rows: continue
		o.extend(map_rows)
	if combine:  o =combine_popups(o)
	if cull: o = cull_maplist(o)
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
	if instance.description:
		m += '<p class="mt-2 mb-0">'+instance.description+'</p>'

	if hasattr(instance,'play_field'):
		link =  getattr(instance,getattr(intance,'play_field'))
		if link:
			m += '<a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" target="_blank" href='
			m += link
			m += 'role="button"><i class="fas fa-play"></i></a>'
	m += instance2map_buttons(instance)
	return m
	

def cull_maplist(maplist):
	o = []
	for line in maplist:
		if line not in o: o.append(line)
	return o
		
