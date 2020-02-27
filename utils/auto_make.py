from catalogue.models import Genre, Text, Publisher, Publication
from persons.models import Person
import datetime
from django.apps import apps
from django.core import exceptions
import math
import pandas as pd
from utils.loc_util import _save_locations as save_model
from utils.loc_util import UserLoc
from utilities.models import Language

def delete_all(name):
	model = apps.get_model('catalogue',name)
	instances = model.objects.all()
	[i.delete() for i in instances]

def make_all(delete_current = False):
	'''Create model instances for several models based on excel files.'''
	if delete_current: 
		names = 'Genre,Binding,Publisher,Text,Publication'.split(',')
		[delete_all(name) for name in names]
	make_genres()
	make_bindings()
	make_publishers()
	make_texts()
	make_publications()


def load_model_instance(name, model_name, app_name, field_name = 'name'):
	'''load a model instance
	name 			string to search model, instances should be seperated with ;
	model_name 		name of the model
	app_name 		name of the app the model belongs to
	field_name 		name of the field to search for the name
	if field_name = 'name' -> model.objects.get(name = name)
	returns list of model instances or model instance
	throws error if instance does not exists
	'''
	if type(name) != str: return None
	names = list(set(name.split(';')))
	output = []
	model = apps.get_model(app_name,model_name)
	for name in names:
		try: output.append(model.objects.get(**{field_name:name}))
		except exceptions.ObjectDoesNotExist: 
			print(field_name,name,'not found in',model_name)
		except exceptions.MultipleObjectsReturned: 
			print('found more than one instance:',
				name,model_name,app_name,field_name)
	if len(output) == 0: return None
	if len(output) == 1: return output[0]
	return output


def make_simple_model(filename = '',column_name = '',model_name='',app_name='',
	values = ''):
	'''Create model instances
	extract a list of string values form excel file
	to create simple instances of the specified model
	if there are multiple instance in a cell these are sperated with a ;
	filename 		filename of excel file
	column_name 	column to be extracted
	model_name 		name of model to create instances of
	app_name 		name of app model belongs to
	'''
	if values == '':
		d = pd.read_excel(filename)
		values = list(set(getattr(d,column_name)))
		print(values)
		o = []
		for v in values:
			if str(v) == 'nan': continue
			if ';' in v: o.extend(v.split(';'))
			else: o.append(v)
		o = [v.strip(' ') for v in o]
		values = list(set(o))
	elif type(values) == str: values = values.split(',')
	print(values)
	model = apps.get_model(app_name,model_name)
	o = [model(name=v) for v in values]
	save_model(o,model_name)
	return o


def make_genres(filename= 'data/Text.xlsx', column_name = 'Genre'):
	'''Create genre instances based on excel file.'''
	return make_simple_model(filename=filename,column_name=column_name,
		model_name = 'Genre',app_name='catalogue')


def names2genres(genre_names= ''):
	'''create genre instances based on csv string.'''
	if genre_names == '': raise ValueError('provide comma seperated genre names')
	genres = genre_names.split(',')
	o = [Genre(name=g) for g in genres]
	save_model(o,'genres')
	return o


def make_bindings(filename= 'data/Publication.xlsx', column_name = 'Form'):
	'''Create binding instances based on excel file.'''
	return make_simple_model(filename=filename,column_name=column_name,
		model_name = 'Binding',app_name='catalogue')


def make_publishers(filename= 'data/Publication.xlsx',column_name='Publisher'):
	'''Create publisher instances based on excel file.'''
	return make_simple_model(filename=filename,column_name=column_name,
		model_name = 'Publisher',app_name='catalogue')


def make_texts(filename_text = ''):
	'''Create text instances based on excel file.'''
	if filename_text == '': filename_text = 'data/Text.xlsx'
	d = pd.read_excel(filename_text)
	o, langauage_error, genre_error = [],[],[]
	for line in d.values:
		l,g =None,None
		text_id,title,language, genre, setting = line
		if type(setting) != str:setting = ''
		l = load_model_instance(language,'Language','utilities')
		g = load_model_instance(genre,'Genre','catalogue')
		o.append(Text(text_id=text_id,title=title,language=l,
			genre=g,setting=setting))
	save_model(o,'texts')
	return langauage_error, genre_error

def intornone(i):
	try: return int(i)
	except: return None

def make_publications(filename_text = ''):
	'''Create publication instances based on excel file.'''
	if filename_text == '': filename_text = 'data/Publication.xlsx'
	d = pd.read_excel(filename_text)
	for line in d.values:
		l,g =None,None
		p_id,title,binding,publisher,date,location,npub,dedication= line
		p = load_model_instance(publisher,'Publisher','catalogue')
		b = load_model_instance(binding,'Binding','catalogue')
		l = load_model_instance(location,'UserLoc','locations')
		o=Publication(publication_id=p_id,title=title,form=b,
			date=intornone(date),location=l)
		s,a,e = save_model([o],'publication',verbose = False)
		if len(s) != 1: continue
		if p == None: continue
		elif type(p) == list: [o.publisher.add(pub) for pub in p]
		else: o.publisher.add(p)
	return o
	
def make_function(filename= 'data/Person.xlsx', column_name = 'Function'):
	return make_simple_model(filename=filename,column_name=column_name,
		model_name = 'Function',app_name='persons')

def make_pseudonym(filename= 'data/Person.xlsx', column_name = 'Pseudonym(s)'):
	return make_simple_model(filename=filename,column_name=column_name,
		model_name = 'Pseudonym',app_name='persons')

def extract_names(s):
	if type(s) == float: return []
	return [x.strip() for x in s.split(';')]

def extract_number(n):
	if type(n) == int: return n
	if type(n) == datetime.datetime: return n.year
	if type(n) == float: return None
	if '-' in n: n = n.split('-')[-1]
	if '/' in n: n = n.split('/')[-1]
	n = ''.join([x for x in n if x.isnumeric()])
	try: return int(n)
	except: return None

def _ms(s):
	if type(s) != str and math.isnan(s): return None
	return str(s)

def set_sex(sex):
	if sex in ['F','M','O']: return sex
	return 'U'


def make_persons(filename_text = 'data/Person.xlsx'):
	d = pd.read_excel(filename_text)
	o = []
	for line in d.values:
		p_id,lname,fname,func,pseud,sex,dob,dod,pob,pod,res,trav,ac,notes = line
		if type(lname) == type(fname) == float: continue
		print([type(lname), type(fname),float])
		print(type(lname) == type(fname) == float)
		pseud = extract_names(pseud)
		pseuds = [load_model_instance(x,'Pseudonym','persons') for x in pseud]
		by, dy = extract_number(dob), extract_number(dod)
		o= Person(first_name=_ms(fname),last_name=_ms(lname),
			sex=set_sex(sex),birth_year=by, death_year=dy,notes= _ms(notes) )
		s,a,e = save_model([o],'Persons',verbose=False)
		if len(s) != 1: continue
		[o.pseudonym.add(pseud) for pseud in pseuds]
		o.save()
	return o
		

def make_personillustrationrelationroles():
	make_simple_model(
		values= 'illustrator,subject',
		model_name='PersonIllustrationRelationRole',
		app_name='persons'
		)

def make_persontextrelationroles():
	make_simple_model(
		values= 'author,translator,editor,subject',
		model_name='PersonTextRelationRole',
		app_name='persons'
		)
	

		
			




	
