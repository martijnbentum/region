from utils.model_util import get_all_models

def get_totals(model_names = ''):
	o = {}
	m = get_all_models(model_names = model_names)
	for x in m:
		o[x._meta.model_name] = x.objects.all().count()
	return o
