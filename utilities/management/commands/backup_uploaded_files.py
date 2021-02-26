from django.core.management.base import BaseCommand
from django.apps import apps
from utils.export import Exports
import time
import os
from utils.backup_util import put_file, isfile
from utils.signal_util import extract_filename_and_path
from utils.model_util import make_models_image_file_dict

'''
backup uploaded files to a werkgroepmap
'''
n = 0
m = 0

class Command(BaseCommand):
	def handle(self, *args, **options):
		start = time.time()
		d = make_models_image_file_dict()
		n = 0
		for k in d:
			app_name, model_name = k
			model = apps.get_model(app_name, model_name)
			for instance in model.objects.all():
				n += handle_instance(instance,d,k)
		print('done')
		delta = time.time() -start
		print('backup of ' + str(n) +' uploaded files took: ',round(delta),' seconds')
		print(str(m) +' files were already backed up')


def handle_instance(instance,d,k,verbose = False):
	global n,m
	for field_name in d[k]:
		field = getattr(instance,field_name)
		if field:
			local_path, remote_path, filename = extract_filename_and_path(field.name)
			if not isfile(remote_path + filename):
				print("file not yet backed up, saving to remote folder")
				put_file(local_path,remote_path,filename)
				n += 1
			else:
				if verbose:print('file is already backed up')
				m +=1
	return n
			
		
		



