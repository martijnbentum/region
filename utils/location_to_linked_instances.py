from django.apps import apps
import glob
import os
import string
from locations.models import Location
import json
from utils.model_util import instance2names

instance_types = 'text,illustration,publication,periodical,movement,publisher'
instance_types += ',person'
instance_types = instance_types.split(',')
directory = '../location_container_instance_links/'

def get_relation_fields(location):
	sets = [field for field in dir(location) if field.endswith('_set')] 
	sets = [field for field in sets if not field.startswith('location')]
	relation_fields = sets
	return relation_fields

def find_relation_field(location, instance_type):
	for field in get_relation_fields(location):
		if field.startswith(instance_type): return field
	return False

def get_all_linked_instances(location):
	output = []
	for field in get_relation_fields(location):
		output.extend( list(getattr(location,field).all()) )
	return output

def get_linked_instances_of_type(location, instance_type,use_publication_link=False):
	'''get all instance of a specific type (e.g. text) linked to a location.'''
	relation_field = find_relation_field(location, instance_type)
	if use_publication_link or not relation_field:
		instances = _get_secondary_linked_instance_of_type(location,instance_type)
		if instances != False: return instances
		elif use_publication_link: 
			print('no link found on publication trying direct route')
	if not relation_field:
		m = instance_type + ' not found in relation fields:\n' 
		m +='\n'.join(get_relation_fields(location)) + '\n'
		m += 'of location:' + str(location) + ' '
		m += 'could not use secondary route through publication\n'
		m += 'as ' + instance_type + ' is not text or illustration'
		raise ValueError(m)
	instances = list(getattr(location,relation_field).all())
	if instance_type == 'person':
		output = []
		for x in instances:
			if x.person not in output:output.append(x.person)
		return output
	return instances

def _get_linked_texts_through_publication_location(location):
	'''text has a location field, but is also linked to an location via publication.
	this function retrieves texts linked to a location based on that location.
	the get_linked_instances_of_type gets the texts directly linked to location
	'''
	return _get_secondary_linked_instance_of_type(location,'text')

def _get_linked_illustrations_through_publication_location(location):
	'''illustration has not location field, this returns the same as 
	get_linked_instances_of_type because a relation_field is not found on
	the location instance
	'''
	return _get_secondary_linked_instance_of_type(location,'illustration')



def _get_secondary_linked_instance_of_type(location, instance_type):
	if instance_type not in ['illustration','text']:
		return False
	publications = get_linked_instances_of_type(location,'publication')
	output = []
	for publication in publications:
		if instance_type == 'illustration':
			temp = publication.illustrationpublicationrelation_set.all() 
			illustrations = [x.illustration for x in temp if x.illustration]
			output.extend( [x for x in illustrations if x not in output])
		elif instance_type == 'text':
			temp = publication.textpublicationrelation_set.all() 
			texts = [x.text for x in temp if x.text]
			output.extend( [x for x in texts if x not in output])
		else: raise ValueError(instance_type,'should be text or illustration')
	return output

def get_instances_linked_to_locations(locations,instance_type,
	use_publication_link=False):
	output = []
	for location in locations:
		x = get_linked_instances_of_type(location,instance_type,use_publication_link)
		if type(x) != list: 
			raise ValueError(x, 'should be type list, type:',type(x))
		output.extend([instance for instance in x if instance not in output]) 
	return output
			
def get_instances_linked_to_locations_contained_in_location(location,
	instance_type, use_publication_link = False, use_presave = True):
	if use_presave:
		print('searching linked instances for:',location)
		presaved = _load_presaved(location,instance_type)
		if presaved != False: 
			print('returning presaved linked instances of type:',instance_type)
			return presaved
	locations = [location]
	locations.extend( [x.contained for x in location.container.all()] )
	return get_instances_linked_to_locations(locations,instance_type,
		use_publication_link)

def get_all_instances_linked_to_contained_location(location):
	output = {}
	ninstances = 0
	for instance_type in instance_types:
		instances = []
		i = get_instances_linked_to_locations_contained_in_location(location,
			instance_type,use_presave = False)
		instances.extend([x for x in i if x not in instances])
		if instance_type == 'text':
			ii=get_instances_linked_to_locations_contained_in_location(location,
				instance_type, use_publication_link=True,use_presave=False)
			instances.extend([x for x in ii if x not in instances])
		output[instance_type] = instance_list_to_repr(instances)
		output[instance_type+'_pk'] = instance_list_to_pk(instances)
		if instances:app_name, model_name = instance2names(instances[0])
		else:app_name, model_name = '',''
		output[instance_type+'_app_name'] = app_name
		output[instance_type+'_model_name'] = model_name
		ninstances += len(instances)
	output['ninstances'] = ninstances
	return output

def _make_pre_save_instances_linked_to_contained_locations():
	locations = list( Location.objects.filter(location_type__name='region') )
	locations.extend( Location.objects.filter(location_type__name='country') )
	print('found',len(locations),'countries and regions')
	locations = [l for l in locations if l.container.all().count() > 50]
	print('handling all regions and countries with over 50 contained locations')
	print(len(locations), 'satisfy this condition')
	if not os.path.isdir(directory): os.mkdir(directory)
	print('removing previous saves')
	os.system('rm ../location_container_instance_links/*_pk-*')
	for i,location in enumerate(locations):
		print('handling location:',location,location.location_type.name)
		print(i, len(locations))
		if location.container.all().count() < 50:
			print('contains small amount of locations, skipping')
			continue
		o = get_all_instances_linked_to_contained_location(location)
		filename = container_location_to_filename(location)
		filename += '_n-' + str(o['ninstances'])
		with open(filename,'w') as fout:
			json.dump(o,fout)
		print('saved:',filename)


def instance_list_to_pk(instances):
	return [x.pk for x in instances]

def instance_list_to_repr(instances):
	return [x.__repr__() for x in instances]

def container_location_to_filename(location):
	n = directory
	name = location.name.lower()
	for x in string.punctuation +' ':
		if x == '-':continue
		name = name.replace(x,'-')
	n += name
	n += '_' + location.location_type.name
	n += '_pk-' + str(location.pk)
	return n


def _load_presaved(location,instance_type):
	o = load_json(location)
	if instance_type == 'all':return o
	if o == False: return False
	if o['ninstances'] == 0: return []
	if instance_type not in o.keys():
		print(instance_type, o.keys(),'could not find instance type in presave')
		return False
	if o[instance_type] == []: return []
	app_name=o[instance_type + '_app_name']
	model_name =o[instance_type + '_model_name']
	print('loading model:',app_name, model_name)
	model = apps.get_model(app_name,model_name)
	instances = model.objects.filter(pk__in = o[instance_type + '_pk'])
	if instances.count() != len(o[instance_type + '_pk']):
		print('discrapency between presaved number',len(o[instance_type + '_pk']))
		print('and number of instances returned from database:',instances.count())
		print('presaved pk list:',o[instance_type + '_pk'])
	return list(instances)


def load_json(location):
	filename = container_location_to_filename(location)
	fn = glob.glob(filename + '*')
	if not len(fn) ==1:
		print(fn,'did not find a single filename, could not load presaved instances')
		return False
	fin = open(fn[0])
	o = json.load(fin)
	return o

	
	


	
	
	
