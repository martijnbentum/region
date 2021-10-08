from django.core.management.base import BaseCommand
from django.db import connection 
from utils import location_to_linked_instances as ltli
import time
import os

'''
CRUDEvent creates an db instance for each change to the database.
This can blow up the size of the database, especially with 
programatic changes to instances.

CRUD events without changes (saving an instance without changing anything
or wihtout a user (programmatic changes) are deleted to save disk space
'''


class Command(BaseCommand):

	def handle(self, *args, **options):
		start = time.time()
		print('pre saving instances linked to regions and countries')
		ltli._make_pre_save_instances_linked_to_contained_locations()
		delta = time.time() -start
		print('pre saving took: ',round(delta),' seconds')




