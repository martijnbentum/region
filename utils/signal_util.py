from django.apps import apps
import sys
from easyaudit.models import CRUDEvent
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from django.conf import settings
from catalogue.models import TextTextRelation
from .model_util import instance2name, instance2names, make_models_image_file_dict
from .backup_util import put_file, isfile

from persons.models import Person,Movement, PersonTextRelation, PersonIllustrationRelation
from persons.models import PublisherManager, PersonPeriodicalRelation, PersonMovementRelation
from catalogue.models import Text,Publication,Publisher,Illustration,Periodical

import sys
import os

def catch_m2m(instance, action, pk_set, model_name,field_name):
	'''Adds a changed field dict to changed_fields attr of easyaudit event object
	in case of m2m changes.
	functions is called by django m2m_changed signal.
	this needs a receiver per m2m field per model, these are made by the 
	model2m2m receiver.
	'''
	z = False
	field = getattr(instance,field_name)
	if action == 'pre_remove':
		before = field.all()
		after = [n for n in field.all() if n.pk not in pk_set]
		z = True
	elif action == 'post_add':
		after= field.all()
		before= [n for n in field.all() if n.pk not in pk_set]
		z = True
	if z:
		# the event object stores changes in the changed_fields as a dict
		# easyaudit does not catch m2m changes, here we update the attr with m2m changes
		event = CRUDEvent.objects.filter(content_type__model = model_name,object_id= instance.pk)
		if event: 
			event = event[0]
			v = {field_name:[','.join([str(n) for n in before]),','.join([str(n) for n in after])]}
			if type(event.changed_fields) != dict: event.changed_fields = v
			else: 
				event.changed_fields.update(v)
			event.save()
		print(model_name,field_name, 'before:',','.join([str(n) for n in before]))
		print(model_name,field_name,'after:',','.join([str(n) for n in after]))
		instance.save()
	

def make_m2mreceiver(sender,model_name,field_name):
	'''creates a receiver for a given m2m field of a model.'''
	m = '@receiver(m2m_changed, sender='+sender+')\n'
	m+= 'def '+sender.replace('.','__').lower() +'(sender,instance,action,**kwargs):\n'
	m+= '\tpk_set = kwargs["pk_set"]\n'
	m+= '\tcatch_m2m(instance,action,pk_set,"'+model_name+'","'+field_name+'")'
	exec(m,globals())

def model2m2mreceiver(model_name,app_name):
	'''creates m2m reciever for each m2m field of a model.'''
	model = apps.get_model(app_name,model_name)
	m2m_fieldnames = model._meta.__dict__['local_many_to_many']
	for f in m2m_fieldnames:
		field_name = f.attname
		sender = model_name+'.'+field_name+'.through'
		make_m2mreceiver(sender,model_name.lower(),field_name)


#list of models with m2m models that need to be tracked by easyaudit.'''
names = 'Text$catalogue,Publication$catalogue,Publisher$catalogue,Illustration$catalogue'
names += ',Person$persons,Movement$persons,Periodical$catalogue'
for name in names.split(','):
	model_name, app_name = name.split('$')
	model2m2mreceiver(model_name,app_name)


#example of a receiver function to cat m2m_changed singals.
'''
@receiver(m2m_changed,sender=Famine.names.through)
def bla(sender, instance,action,**kwargs):
	pk_set = kwargs['pk_set']
	catch_m2m(instance,action,pk_set,'famine','names')
'''

@receiver(post_delete,sender = TextTextRelation)
def show(sender,instance,**kwargs):
	print(instance,'post_delete',instance.pk,instance.primary,instance.secondary)
	print(instance2names(instance.primary),instance2names(instance.secondary))
	a,m = instance2names(instance)
	pan, pmn=instance2names(instance.primary)
	sap,smn =instance2names(instance.secondary)
	print(instance.pk,instance.primary.pk,instance.secondary.pk)
	print(instance.__str__())
	print(instance.primary.__str__())
	print(instance.secondary.__str__())
	print(m,pmn,smn)
	c = CRUDEvent.objects.filter(content_type__model = m.lower(),object_id=instance.pk)
	pe = CRUDEvent.objects.filter(content_type__model = pmn.lower(),object_id=instance.primary.pk)[0]
	se = CRUDEvent.objects.filter(content_type__model = smn.lower(),object_id=instance.secondary.pk)[0]
	v = {'TextTextRelation':[instance.__str__(),"(deleted)"]}
	if type(pe.changed_fields) == dict:pe.changed_fields.update(v)
	else: pe.changed_fields = v
	if type(se.changed_fields) == dict:se.changed_fields.update(v)
	else:se.changed_fields=v
	pe.save()
	se.save()
	try:
		print(c[0].get_event_type_display(),c[0].changed_fields,len(c))
		print(pe.get_event_type_display(),pe.changed_fields)
		print(se.get_event_type_display(),se.changed_fields)
	except: print('could not print info',sys.exc_info())

def make_file_backup_postsave_receiver(app_name,model_name):
	m = '@receiver(post_save, sender = '
	m += model_name + ')\n'
	m += 'def save_file_backup_'+app_name + '_' + model_name 
	m += '(sender, instance, **kwargs):\n'
	m += '\tif os.path.isfile("data/no_backup_on_save"):return\n'
	m += '\tfieldnames = make_models_image_file_dict()["'
	m += app_name + '","'+model_name +'"]\n'
	m += '\tfor field_name in  fieldnames:\n'
	m += '\t\tprint("handling field:",field_name)\n'
	m += '\t\tfield = getattr(instance,field_name)\n'
	m += '\t\tif field:\n'
	m += '\t\t\tlocal_path, remote_path, filename = extract_filename_and_path(field.name)\n'
	m += '\t\t\tprint(local_path, remote_path, filename)\n'
	m += '\t\t\tif not isfile(remote_path + filename):\n'
	m += '\t\t\t\tprint("file not yet backed up, saving to remote folder")\n'
	m += '\t\t\t\tput_file(local_path,remote_path,filename)\n'
	m += '\t\t\telse: print("backup file already exists, doing nothing")\n'
	exec(m,globals())


#create receivers for all models that have upload file fields to make backups of the image
d = make_models_image_file_dict()
for k in d:
	app_name, model_name = k
	make_file_backup_postsave_receiver(app_name,model_name)

#create filename and path to make a backup to the werkgroepmap
def extract_filename_and_path(name):
	'''create correct path and filename to backup to the werkgroep map'''
	media_dir = settings.MEDIA_ROOT
	media_remote_dir = media_dir.split('/')[-1]
	if not media_dir.endswith('/'): media_dir += '/'
	if not media_remote_dir.endswith('/'): media_remote_dir += '/'
	if '/' not in name: filename, remote_path = name, ''
	else: filename, remote_path = name.split('/')[-1], '/'.join(name.split('/')[:-1])
	remote_path += '/'
	local_path = media_dir + remote_path
	name = local_path + '/' + filename
	remote_path = media_remote_dir + remote_path
	if not os.path.isdir(local_path):print(local_path,'not an existing directory') 
	if not os.path.isfile(name):print(name,'not an existing file')
	return local_path, remote_path, filename

# receivers to set person field on text, illustration, publisher, periodical and movement
# person field is combination of first name last name and pseudonyms of each person
# linked to a specific entry
@receiver([post_save,post_delete],sender = PersonTextRelation)
def update_person_on_text(sender,instance,**kwargs):
	instance.text._set_person()

@receiver([post_save,post_delete],sender = PersonIllustrationRelation)
def update_person_on_illustration(sender,instance,**kwargs):
	instance.illustration._set_person()

@receiver([post_save,post_delete],sender = PublisherManager)
def update_person_on_publisher(sender,instance,**kwargs):
	instance.publisher._set_person()

@receiver([post_save,post_delete],sender = PersonPeriodicalRelation)
def update_person_on_periodical(sender,instance,**kwargs):
	instance.periodical._set_person()

@receiver([post_save,post_delete],sender = PersonMovementRelation)
def update_person_on_movement(sender,instance,**kwargs):
	instance.movement._set_person()

