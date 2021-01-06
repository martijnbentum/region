from .model_util import instance2name, instance2names
import random

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
	
def pop_up(instance,latlng=None, extra_information= ''):
	'''create a pop up based on the instance'''
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
	m += extra_information

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
icons ='far fa-file-alt,fa fa-picture-o,far fa-building,fa fa-book'
icons +=',fa fa-newspaper-o,fa fa-male,fa fa-users'
icons = ['<i class="'+icon+' fa-lg mt-2" aria-hidden="true"></i>' for icon in icons.split(',')]
color_dict,icon_dict ={}, {}
for i,name in enumerate(names):
	color_dict[name] = colors[i]
	icon_dict[name] = icons[i]
		
