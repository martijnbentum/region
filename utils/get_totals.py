from utils.model_util import get_all_models
import glob

def get_totals(model_names = ''):
	o = {}
	m = get_all_models(model_names = model_names)
	for x in m:
		o[x._meta.model_name] = x.objects.all().count()
	return o

def get_countries():
	fn = glob.glob('../location_container_instance_links/*country*')
	output = []
	for f in fn:
		n = int(f.split('_n-')[-1])
		filename = f.split('/')[-1].split('_')[0].replace('-',' ').title()
		if n > 0:output.append([filename,n])
	output =sorted(output, key=lambda x: x[1],reverse = True)
	output = [line[0] for line in output]
	return output


