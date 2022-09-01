from django.core.management.base import BaseCommand
from django.db import connection 
from utils import location_to_linked_instances as ltli
import time
import os

'''
it slow to retrieve all instances linked to a region /country
therefore these links are pre saved
'''


class Command(BaseCommand):

    def handle(self, *args, **options):
        start = time.time()
        print('pre saving instances linked to regions and countries')
        ltli._make_pre_save_instances_linked_to_contained_locations()
        delta = time.time() -start
        print('pre saving took: ',round(delta),' seconds')




