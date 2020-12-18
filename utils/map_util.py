from .model_util import instance2name, instance2names
import random

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
				name = rl.other_field_name(source_model_name)
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
				mr = instance2maprows(instance,latlng=l.latlng,pop_up=instance.pop_up(),role=role)
				map_list.append(mr)
	return locations,field_names,map_list
	

def field2locations(instance, field_name):
	'''return locations from a field (fk or m2m) on a model.'''
	if not hasattr(instance,field_name):return None
	x = getattr(instance,field_name)
	location_model = apps.get_model('locations','Location')
	if type(x) == Location: return [x]
	if 'ManyRelatedManager' in str(type(x)): 
		return x.all()
	# print('field:',field_name,'on:',instance,'is of unknown type:',type(x))
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
	if pop_up == None:pop_up = instance.pop_up()
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


def get_location_name(instance,latlng):
	location_name = ''
	if latlng==None: return location_name
	if hasattr(instance,'gps'):
		for i,gps in enumerate(instance.gps.split(" | ")):
			if not gps: continue
			print(latlng,gps)
			if latlng == eval(gps):
				location_name=instance.gps_names.split(" | ")[i]
	return location_name
	
def pop_up(instance,latlng=None):
	# location_name = get_location_name(instance,latlng)
	location_name = instance.latlng2name(latlng)
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
	if location_name:m += '<p><small>'+location_name+'</small></p>'
	return m

def gps2latlng(gps,return_one = False):
	'''converts string with gps coordinates to tuple(s) of floats
	gps 		string with format '43.2, 4.2' or '5.3, 4.5 | 6.4, 3.1'
	output 		tuple/list of tuples of floats (43.2, 4.2) or [(5.3, 4.5), (6.4, 3.1)] 
	'''
	try:
		o = [eval(x) for x in gps.split(' | ')]
		if len(o) == 1 or return_one: o = o[0]
	except: 
		print('could not convert gps > latlng, input:',gps)
		o = None
	return o
	
def latlng2gps(latlng):
	'''converts tuple or list of tuples with gps coordinates to string
	latlng 		tuple/list of tuples of floats (43.2, 4.2) or [(5.3, 4.5), (6.4, 3.1)] 
	output 		string with format '43.2, 4.2' or '5.3, 4.5 | 6.4, 3.1'
	'''
	if type(latlng) == tuple and len(latlng) == 2:
		return str(latlng)
	if type(latlng) == list:
		error = False
		for x in latlng:
			if type(x) != tuple or len(x) != 2:error = True
		if not error: return ' | '.join(map(str,latlng))
	print('could not convert latlng > gps, input:',latlng)
	return ''	

def cull_maplist(maplist):
	o = []
	for line in maplist:
		if line not in o: o.append(line)
	return o


def instance2color(instance):
	name = instance2name(instance).lower()
	if name in color_dict.keys(): return color_dict[name]
	else: return 'black'

def instance2icon(instance):
	name = instance2name(instance).lower()
	if name in icon_dict.keys():
		return icon_dict[name]
	return 'not found'

def instance2map_buttons(instance):
	app_name,model_name= instance2names(instance)
	m = ''
	m += '<a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" href='
	m += '/'+app_name+'/edit_' + model_name.lower()+'/' + str(instance.pk) 
	m += ' role="button"><i class="far fa-edit"></i></a>'
	m += '<a class = "btn btn-link btn-sm mt-1 pl-0 text-dark"'# href='
	# m += '/locations/show_links/'+app_name+'/'+ model_name.lower()+'/' + str(instance.pk) +'/'
	m += ' onclick="getLinks()"'
	m += ' role="button"><i class="fas fa-project-diagram"></i></a>'
	return m

names = 'text,illustration,publisher,publication,periodical,person,movement'.split(',')
colors = '#0fba62,#5aa5c4,#e04eed,#ed4c72,#1e662a,#c92f04,#e39817'.split(',')
icons ='fa fa-file-text-o,fa fa-picture-o,fa fa-building-o,fa fa-book'
icons +=',fa fa-newspaper-o,fa fa-male,fa fa-users'
icons = ['<i class="'+icon+' fa-lg mt-2" aria-hidden="true"></i>' for icon in icons.split(',')]
color_dict,icon_dict ={}, {}
for i,name in enumerate(names):
	color_dict[name] = colors[i]
	icon_dict[name] = icons[i]
		
