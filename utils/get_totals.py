from django.apps import apps
from utils.model_util import get_all_models
import glob
import os
import time
import json

to_old_seconds = 3600 * 24 * 7
directory = 'link_data/totals/'

def get_totals(model_names = ''):
	o = {}
	m = get_all_models(model_names = model_names)
	for x in m:
		o[x._meta.model_name] = x.objects.all().count()
	return o

def get_periodical_countries():
	filename = 'periodical_percentage_countries'
	d, to_old = check_load(filename)
	if not to_old: return d
	print('computing the percentage breakdown of countries for Periodicals')
	Periodical= apps.get_model('catalogue','Periodical')
	d = {}
	for x in Periodical.objects.all():
		locations =  x.location.all()
		for location in locations:
			country = location.country
			if country:
				if country not in d.keys():d[country] =1
				else: d[country] +=1
	d = count_dict_to_sorted_perc_dict(d)
	save_total(d,filename)
	return d

def check_load(filename):
	if not os.path.isdir(directory): os.mkdir(directory)
	f = directory + filename
	if not os.path.isfile(f): return None, True
	# if last modification is longer then a week ago
	if time.time() - os.path.getmtime(f) > to_old_seconds:
		return None, True
	else: return json.load(open(f)), False

def save_total(d,filename):
	print('saving:',filename)
	if not os.path.isdir(directory): os.mkdir(directory)
	fout = open(directory + filename, 'w')
	json.dump(d,fout)
				

def get_countries(totals = None):
	if totals == None: totals = sum(get_totals().values())
	fn = glob.glob('link_data/location_container_instance_links/*country*')
	output = []
	for f in fn:
		n = int(f.split('_n-')[-1])
		perc = round(n / totals * 100,2)
		filename = f.split('/')[-1].split('_')[0].replace('-',' ').title()
		if n > 0:output.append([filename,perc])
	output =sorted(output, key=lambda x: x[1],reverse = True)
	d = dict(output)
	return d

def get_perc_gender():
	Person = apps.get_model('persons','Person')
	p = Person.objects.all()
	sex = [x.sex for x in p]
	genders = list(set(sex))
	npersons = p.count()
	temp = []
	for gender in genders:
		perc = round(sex.count(gender) /npersons *100,2)
		temp.append([gender,perc])
	temp = sorted(temp,key=lambda x:x[1],reverse=True)
	d = dict(temp)
	return d

def get_perc_text_genres():
	return _make_category_dict('Text','Genre','catalogue')

def get_perc_text_types():
	d= _make_category_dict('Text','TextType','catalogue')
	original = 100 - sum(d.values())
	o = ({'original':original})
	for key,value in d.items():
		o[key] = value
	return o


def get_perc_publication_types():
	return _make_category_dict('Publication','PublicationType',
		'catalogue')

def get_perc_illustration_categories():
	return _make_category_dict('Illustration','IllustrationCategory',
		'catalogue')

def get_perc_illustration_types():
	d= _make_category_dict('Illustration','IllustrationType','catalogue')
	original = 100 - sum(d.values())
	o = ({'original':original})
	for key,value in d.items():
		o[key] = value
	return o

def get_perc_movement_types():
	return _make_category_dict('Movement','MovementType','persons')

def _make_category_dict(base_model_name,category_model_name,
	app_name = 'catalogue'):
	base_model= apps.get_model(app_name,base_model_name)
	category_model= apps.get_model(app_name,category_model_name)
	nbase_instances= base_model.objects.all().count()
	category_instances= category_model.objects.all()
	temp = []
	for instance in category_instances:
		category = category_model_name == 'IllustrationCategory'
		if base_model_name == 'Illustration' and category: 
			n = getattr(instance,base_model_name).all().count()
		else:
			n = getattr(instance,base_model_name.lower() + '_set').all().count()
		perc = round(n/nbase_instances*100,2)
		if n > 0:temp.append([instance.name.lower(), perc])
	temp = sorted(temp,key=lambda x:x[1],reverse=True)
	d = dict(temp)
	return d


def count_dict_to_sorted_perc_dict(d):
	total = sum(d.values())
	o = []
	for key,value in d.items():
		o.append([key,round(value /total *100,2)])
	o= sorted(o,key=lambda x:x[1],reverse=True)
	return dict(o)




'''
def get_perc_text_genres():
	Text = apps.get_model('catalogue','Text')
	Genre = apps.get_model('catalogue','Genre')
	ntexts = Text.objects.all().count()
	genres = Genre.objects.all()
	temp = []
	for genre in genres:
		n = genre.text_set.all().count()
		perc = round(n/ntexts *100,2)
		if n > 0:temp.append([genre.name.lower(), perc])
	temp = sorted(temp,key=lambda x:x[1],reverse=True)
	d = dict(temp)
'''

