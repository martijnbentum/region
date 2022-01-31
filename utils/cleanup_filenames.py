import os
import dcl

def rename_file(instance,file_fieldname,new_name, overwrite = False):
	file_field = getattr(instance,file_fieldname)
	old_path = file_field.path
	base_dir = old_path.replace(file_field.name,'')
	new_path = base_dir + new_name
	if not overwrite: assert not os.path.isfile(new_path)
	os.rename(old_path,new_path)
	setattr(instance,file_fieldname,new_name)
	instance.save()

def remove_diacritics_filename_existing_file(instance,file_fieldname):
	file_field = getattr(instance,file_fieldname)
	if not dcl.has_diacritics(file_field.name):return
	new_name = dcl.clean_diacritics(file_field.name)
	rename_file(instance,file_fieldname,new_name)
	print(new_name[-10:],'updated filename')

def rename_all_dicritic_illustration_filenames():
	from catalogue.models import Illustration
	i = Illustration.objects.all()
	for x in i:
		if not x.upload: continue
		remove_diacritics_filename_existing_file(x,'upload')

def remove_diacritics_filename(filename):
	return dcl.clean_diacritics(filename)



