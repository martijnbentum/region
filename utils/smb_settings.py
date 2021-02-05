cmd = 'smbclient'
host = '//cnas.ru.nl/Wrkgrp'
credf = '-A'
cred = '~/.smbclient.conf'
domainf = '-W'
domain = 'RU'
directoryf = '-D'
directory = 'Region/BACKUP/'
commandf = '-c'

smb = [cmd,host,credf,cred,domainf,domain,directoryf,directory,commandf]
