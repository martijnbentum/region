import os

flag = 'data/no_backup_on_save'

def remove_no_backup_save_flag():
    if os.path.isfile(flag):
        os.remove(flag)
    print('removed flag')

def set_no_backup_save_flag():
    with open(flag, 'w') as fout:
        pass
