from django.core.management.base import BaseCommand
from django.db import connection 
from utils import instances_to_linked_instances 
from utils import map_util
import time
import os

'''
map filtering needs links between many instances which can be 
slow because of many database calls
pre saving links into json dict speeds up map filtering
'''


class Command(BaseCommand):

    def handle(self, *args, **options):
        start = time.time()
        print('pre saving json dicts to speed up map filtering')
        instances_to_linked_instances.make_all()
        map_util.locationtype_filter_dict(save = True)
        delta = time.time() -start
        print('pre saving took: ',round(delta),' seconds')




