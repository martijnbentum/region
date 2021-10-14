from django.apps import apps
from utils.model_util import get_all_models
import glob

def get_totals(model_names = ''):
	o = {}
	m = get_all_models(model_names = model_names)
	for x in m:
		o[x._meta.model_name] = x.objects.all().count()
	return o

def get_countries(totals = None):
	if totals == None: totals = sum(get_totals().values())
	fn = glob.glob('../location_container_instance_links/*country*')
	output = []
	for f in fn:
		n = int(f.split('_n-')[-1])
		perc = round(n / totals * 100,2)
		filename = f.split('/')[-1].split('_')[0].replace('-',' ').title()
		if n > 0:output.append([filename,perc])
	output =sorted(output, key=lambda x: x[1],reverse = True)
	d = dict(output)
	return d

def get_perc_female_persons():
	Person = apps.get_model('persons','Person')
	p = Person.objects.all()
	npersons = p.count()
	nfemales = len([x for x in p if x.sex == 'female'])
	perc_females = round(nfemales / npersons * 100,2)
	return perc_females

def get_perc_text_genres():
	return _make_category_dict('Text','Genre','catalogue')

def get_perc_publication_types():
	return _make_category_dict('Publication','PublicationType','catalogue')

def get_perc_illustration_types():
	return _make_category_dict('Illustration','IllustrationCategory','catalogue')

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
		if base_model_name == 'Illustration':
			n = getattr(instance,base_model_name).all().count()
		else:
			n = getattr(instance,base_model_name.lower() + '_set').all().count()
		perc = round(n/nbase_instances*100,2)
		if n > 0:temp.append([instance.name.lower(), perc])
	temp = sorted(temp,key=lambda x:x[1],reverse=True)
	d = dict(temp)
	return d



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

