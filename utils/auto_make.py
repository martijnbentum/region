from catalogue.models import Genre, Text, Publisher, Publication
from django.apps import apps
import pandas as pd
from utils.loc_util import _save_locations as save_model
from utils.loc_util import UserLoc
from utilities.models import Language

def make_all():
	'''Create model instances for several models based on excel files.'''
	make_genres()
	make_bindings()
	make_publishers()


def load_model_instance(name, model_name, app_name, field_name = 'name'):
	'''load a model instance
	name 			string to search model
	model_name 		name of the model
	app_name 		name of the app the model belongs to
	field_name 		name of the field to search for the name
	if field_name = 'name' -> model.objects.get(name = name)
	returns list of model instances or model instance
	throws error if instance does not exists
	'''
	names = name.split(';')
	output = []
	model = apps.get_model(app_name,model_name)
	for name in names:
		output.append(model.objects.get(**{field_name:name}))
	if len(output) == 1: return output[0]
	return output


def make_simple_model(filename = '',column_name = '',model_name='',app_name=''):
	'''Create model instances
	extract a list of string values form excel file
	to create simple instances of the specified model
	if there are multiple instance in a cell these are sperated with a ;
	filename 		filename of excel file
	column_name 	column to be extracted
	model_name 		name of model to create instances of
	app_name 		name of app model belongs to
	'''
	d = pd.read_excel(filename)
	values = list(set(getattr(d,column_name)))
	o = []
	for v in values:
		if str(v) == 'nan': continue
		if ';' in v: o.extend(v.split(';'))
		else: o.append(v)
	values = o
	model = apps.get_model(app_name,model_name)
	o = [model(name=v.strip(' ')) for v in values]
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
		try: l = Language.objects.get(name = language)
		except: langauage_error.append(line)
		try:g = Genre.objects.get(name = genre)
		except: genre_error.append(line)
		o.append(Text(text_id=text_id,title=title,language=l,
			genre=g,setting=setting))
	save_model(o,'texts')
	if len(langauage_error) > 0 or len(genre_error) > 0:
		print('some languages or genres were not recognized')
	return langauage_error, genre_error


def make_publications(filename_text = ''):
	'''Create publication instances based on excel file.'''
	if filename_text == '': filename_text = 'data/Publication.xlsx'
	d = pd.read_excel(filename_text)
	o, publisher_error, binding_error, location_error = [],[],[],[]
	for line in d.values:
		l,g =None,None
		p_id,title,binding,publisher,date,location,npub,dedication= line
		try: p = publisher.objects.get(name = publisher)
		except: publisher_error.append(line)
		try:b = Binding.objects.get(name = binding)
		except: binding_error.append(line)
		try: l = UserLoc.objects.get(name = location)
		except: location.append(line)
		o.append(Publication(publication_id=p_id,title=title,binding=binding,
			date=date,location=location))
	save_model(o,'texts')
	if len(publisher_error) > 0 or len(binding_error) > 0:
		print('some publishers or bindings were not recognized')
	return publisher_error, binding_error
	
	
