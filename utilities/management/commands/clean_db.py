from easyaudit.models import CRUDEvent
from django.core.management.base import BaseCommand
from django.db import connection 
from utils.export import Exports
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
		print('cleaning database by removing superious CRUD events')
		print('and VACUUM the database')
		dbsize_before = get_db_size()
		print('database size:',dbsize_before,'MB')
		c = CRUDEvent.objects.all()
		print(c.count(),'CRUD events')

		o = []
		for event in c:
			if not event.user or event.changed_fields == 'null': o.append(event)
		print('removing',len(o),'spurious CRUD events') 
		print('(without user or changed fields)')
		for event in o:
			event.delete()

		#clean the database after removing db items
		cursor = connection.cursor()
		cursor.execute("VACUUM")

		dbsize= get_db_size()
		print('database size:',dbsize,'MB, removed:',dbsize_before - dbsize,'MB')
		delta = time.time() -start
		print('cleaning took: ',round(delta),' seconds')




def get_db_size():
	return round(os.path.getsize('db.sqlite3') / 1024 ** 2)
