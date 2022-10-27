from django.core.management.base import BaseCommand
from utils import update_prestored_links
from utils import set_no_backup_save_flag
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
        print('setting no backup flag')
        set_no_backup_save_flag.set_no_backup_save_flag()
        print('updating links prestored on individual instances')
        update_prestored_links.update_all()
        delta = time.time() -start
        print('updating took: ',round(delta),' seconds')
        set_no_backup_save_flag.remove_no_backup_save_flag()
        print('removed no backup flag') 




