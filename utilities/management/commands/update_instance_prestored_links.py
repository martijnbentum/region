from django.core.management.base import BaseCommand
from django.db import connection 
from utils import update_prestored_links
import time
import os

'''
map filtering needs links between many instances which can be 
slow because of many database calls
pre saving links on instances speeds up map filtering
'''


class Command(BaseCommand):

    def handle(self, *args, **options):
        start = time.time()
        print('updating links prestored on individual instances')
        update_prestored_links.update_publication_text_illustration()
        delta = time.time() -start
        print('updating took: ',round(delta),' seconds')




