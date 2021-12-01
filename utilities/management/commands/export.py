from django.core.management.base import BaseCommand
from utils.export import Exports
import time
import os

'''
Export entire database to xlsx / xlm / json file
Filename is region_[date]

At the current db size this takes a minute or two

-output 		filetypes xlsx / xlm / json
-path 			destination folder (checked to exist, 
				otherwise saved in repository directory)
--dryrun 		do not actually create export and save files, 
				but run through everything else
				(print filename and path)
'''

class Command(BaseCommand):
	def add_arguments(self,parser):
		parser.add_argument('-output',nargs='+')
		parser.add_argument('-path')
		parser.add_argument('-filename')
		parser.add_argument('--dryrun',action='store_true')


	def handle(self, *args, **options):
		start = time.time()
		save = True if not options['dryrun'] else False
		path = options['path']  
		path = path if path and os.path.isdir(path) else ''
		if path != '' and not path.endswith('/'): path += '/'
		filename = options['filename']
		print(filename,999,options['filename'],path)
		if not filename: filename = path + 'region_'+time.strftime('%Y_%m_%d_%H_%M')
		else: filename = path + filename
		print('exporting the database...')

		if options['output']:print('filetypes: ',', '.join(options['output']))
		if save:
			export = Exports()
			export.make_exports()
		if 'xlsx' in options['output']:
			print('saving excel file:',filename)
			if save: export.to_excel(filename = filename + '.xlsx')
		if 'xml' in options['output']:
			print('saving xml file:',filename)
			if save:
				with open(filename + '.xml', 'w') as fout:
					fout.write(export.xml_str)
		if 'json' in options['output']:
			print('saving json file:',filename)
			if save:
				with open(filename + '.json', 'w') as fout:
					fout.write(export.json_str)
		print('done')
		if not save: print('no files saved, this was a dryrun')
		delta = time.time() -start
		print('exporting took: ',round(delta),' seconds')
		
		



