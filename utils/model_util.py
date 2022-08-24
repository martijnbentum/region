from django.apps import apps
import random
import string
import itertools
from utils.general import sort_count_dict, sort_dict_on_keys
import time


n='text,publication,periodical,publisher,illustration,person,movement'.split(',')

class info():
	'''inherit from this class to add extra viewing functionality for models'''

	HEADER = '\033[95m'
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	END = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

	def view(self):
		'''show all attributes of instance'''
		print(self.UNDERLINE,self.__class__,self.END)
		n = max([len(k) for k in self.__dict__.keys()]) + 3
		for k in self.__dict__.keys():
			print(k.ljust(n),self.BLUE,self.__dict__[k], self.END)

	@property
	def info(self):
		n = max([len(k) for k in self.__dict__.keys()]) + 3
		m = '<table class="table table-borderless" >'
		for k in self.__dict__.keys():
			if k == '_state' or k == 'id': continue
			m += '<tr class="d-flex">'
			m += '<th class="col-2">'+k.ljust(n)+'</th>'
			m += '<td class="col-8">'+str(self.__dict__[k]) +'</td>'
		m += '</table>'
		return m

	


def id_generator(id_type= 'letters', length = 9):
	'''probably obsolete, generate a random identifier string for an isntance.'''
	if id_type == 'letters':
		return ''.join(random.sample(string.ascii_letters*length,length))
	if id_type == 'numbers':
		return int(''.join(random.sample('123456789'*length,length)))


def compare_model_dicts(sd,od):
	'''Compare model class dictionary to compare the similarity of two model instances.
	helper function of compare_instances
	'''
	equal,similar = True, True
	ntotal,nsame,nsimilar = len(sd.keys())-2, 0, 0
	for k in sd.keys():
		if k in ['id','_state']:continue # skip fields that are different by definition
		if sd[k] == od[k]: 
			nsame +=1
			nsimilar +=1
		elif sd[k] in ['',None] or od[k] in ['',None]: 
			equal = False
			nsimilar +=1
		else: 
			equal,similar = False,False
	perc_same,perc_similar = nsame/ntotal,nsimilar/ntotal
	return equal,perc_same,similar,perc_similar

def compare_instances(self,other):
	'''Compare two instances.
	If each field for the two instances are identical returns equal true

	If fields for the instances only differs  whereby one has default empty value (i.e. none or '')
	return similar true

	Also returns percentage for both equal and similar
	'''
	if type(self) != type(other):
		# print(self,'is not of the same type as:',other,type(self),type(other))
		return False,0,False,0
	sd, od = self.__dict__, other.__dict__
	return compare_model_dicts(sd,od)

def compare_queryset(qs):
	'''Compare all unordered paired combinations of instances in a queryset a
	determines the equality / similarity of the pair. (see compare_ instances)
	'''
	equal_list,similar_list,complete_list = [],[],[]
	for a,b in itertools.combinations(qs,2): #create all unordered paired combinations in the qs
		equal,pe,similar,ps = compare_instances(a,b)
		line = [a,b,equal,pe,similar,ps]
		if equal: equal_list.append(line)
		if similar: similar_list.append(line)
		complete_list.append(line)
	return equal_list, similar_list, complete_list
		

def instance2names(instance):
	# s = str(type(instance)).split("'")[-2]
	# app_name,_,model_name = s.split('.')
	app_name,model_name = instance._meta.app_label, instance._meta.model_name.capitalize()
	return app_name, model_name

def instance2name(instance):
	app_name, model_name = instance2names(instance)
	return model_name
	
		
def copy_complete(instance, commit = True):
	'''copy a model instance completely with all relations.'''
	copy = simple_copy(instance, commit)
	app_name, model_name = instance2names(instance)
	for f in copy._meta.get_fields():
		if f.one_to_many:
			for r in list(getattr(instance,f.name+'_set').all()):
				rcopy = simple_copy(r,False,False)
				setattr(rcopy,model_name.lower(), copy)
				rcopy.save()
		if f.many_to_many:
			getattr(copy,f.name).set(getattr(instance,f.name).all())
	return copy


def simple_copy(instance, commit = True,add_copy_suffix = True):
	'''Copy a model instance and save it to the database.
	m2m and relations are not saved.
	'''
	app_name, model_name = instance2names(instance)
	model = apps.get_model(app_name,model_name)
	copy = model.objects.get(pk=instance.pk)
	copy.pk = None
	print('copying...')
	for name in 'title,name,caption,first_name'.split(','):
		if hasattr(copy,name):
			print('setting',name)
			copy.view()
			setattr(copy,name,getattr(copy,name)+ ' !copy!')
			copy.view()
			break
	if commit:
		copy.save()
	return copy
		

def make_models_image_file_dict():
	'''
	creates a dictionary with all models containing a image or file field.
	dict contents:
	key 		app_name, model name (tuple)
	value 		list of field_names (can either be image or file field
	'''
	from .export import all_models, selected_models
	
	d = {}
	for model in selected_models:
		fields = model._meta.get_fields()
		file_field_names = []
		for field in fields:
			if field.get_internal_type() == 'FileField':
				file_field_names.append(field.name)
		if file_field_names: 
			app_name, model_name = instance2names(model)
			d[app_name, model_name] = file_field_names
	return d

def get_empty_fields(instance,fields = [],default_is_empty =False):
	if not fields: fields = instance._meta.fields
	empty_values = ['',None]
	exclude = 'gps,gps_names'.split(',')
	empty_fields = []
	for f in fields:
		if type(f) == str: f = instance._meta.get_field(f)
		if f.name in exclude:continue
		empty = False
		value = getattr(instance,f.name)
		if value in empty_values:empty = True 
		if not empty and default_is_empty: 
			default = f.get_default()
			if value == default: empty = True
		if empty: empty_fields.append(f.name)
	return empty_fields


def get_all_models(model_names =''):
	if model_names == '': model_names = n
	if type(model_names) == str: model_names = model_names.split(',')
	model_names = [n.lower() for n in model_names]
	all_models = apps.get_models()
	models = []
	for model_name in model_names:
		for model in all_models:
			if model._meta.model_name == model_name: models.append(model)
	return models
		
def get_all_instances(model_names = ''):
	models = get_all_models(model_names= model_names)
	instances =[]
	for x in models:
		instances.extend(x.objects.all())
	return instances

def _make_modelnames():
	model = apps.get_model('utilities','Modelname')
	models = get_all_models()
	for m in models:
		model_name = m._meta.model_name
		app_name = m._meta.app_label
		qs = model.objects.filter(model_name=model_name)
		if not qs:
			print('creating:',model_name)
			x = model(model_name=model_name,app_name=app_name)
			x.save()
		else:print(name,'already exists')


def identifier2instance(identifier):
	app_name, model_name, pk = identifier.split('_')
	model = apps.get_model(app_name,model_name)
	return model.objects.get(pk=pk)
	
def identifiers2instances(identifiers):
	d = {}
	for identifier in identifiers:
		app_name,model_name, pk = identifier.split('_')
		name = model_name,app_name
		if not name in d.keys(): d[name] =[]
		if pk not in d[name]:d[name].append(pk)
	instances = []
	for key, value in d.items():
		model_name,app_name = key
		model = apps.get_model(app_name,model_name)
		instances.extend(model.objects.filter(pk__in=value))
	return instances


def _add_to_count_instance_dict(count_d,instances_d,names, instance):
	for name in names:
		if name not in count_d.keys(): count_d[name] ,instances_d[name] = 0, []
		count_d[name] +=1
		instances_d[name].append(instance)

def instances2model_counts(instances):
	'''names and counts of models that are linked to a list of instance.'''
	count_d = {}
	instances_d = {}
	for instance in instances:
		name = instance2name(instance)
		_add_to_count_instance_dict(count_d,instances_d,[name],instance)
	count_d = sort_count_dict(count_d)
	return count_d, instances_d

def _instances2attribute_counts(instances, identifier2attribute_dict):
    count_d = {}
    instances_d = {}
    d = identifier2attribute_dict
    for instance in instances:
        if instance.identifier not in d.keys(): continue
        names = d[instance.identifier]
        if type(names) != list: names = [names]
        _add_to_count_instance_dict(count_d,instances_d,names,instance)
    count_d = sort_count_dict(count_d)
    return count_d, instances_d

def instances2texttype_counts(instances):
    from . import instances_to_linked_instances as itli
    d = itli.load_json_texttype()
    count_d, instances_d = _instances2attribute_counts(instances,d)
    return count_d, instances_d

def instances2language_counts(instances, languages = None):
    from . import instances_to_linked_instances as itli
    d = itli.load_json_language()
    if languages == None: 
        languages = 'English,French,German,Dutch,Swedish,Danish'
        languages += ',Italian'
        languages = languages.split(',')
    count_d, instances_d = _instances2attribute_counts(instances,d)
    language_keys = list(count_d.keys())
    for language in language_keys:
        if language not in languages:
            del count_d[language]
            del instances_d[language]
    return count_d, instances_d

def instances2genre_counts(instances):
    from . import instances_to_linked_instances as itli
    d = itli.load_json_genre()
    count_d, instances_d = _instances2attribute_counts(instances,d)
    return count_d, instances_d

def instances2gender_counts(instances):
    from . import instances_to_linked_instances as itli
    d = itli.load_json_gender()
    count_d, instances_d = _instances2attribute_counts(instances,d)
    return count_d, instances_d
    
		
	

		 



