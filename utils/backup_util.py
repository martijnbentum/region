import os
import subprocess
from .smb_settings import smb
import random
from string import ascii_lowercase 

smbouputdir = '/var/www/smboutput/'

def make_name():
	'''creates a random name for the smbclient output file.'''
	return ''.join(random.sample(ascii_lowercase *10,30))

def catch_output(name):
	'''saves smbclient output to teext file.'''
	return ' > ' + smbouputdir + name

def get_output(name):
	'''fetches output from the smbclient call'''
	return open(smbouputdir + name).read()

def _mkdir(name, verbose = False):
	'''Create a directory in the remote directory HOHrepositoryfiles
	name 		name of the directory e.g. media/text
	the function assumes that only the lowest most directory does not exists
	If name == media/text the media directory should exists, otherwise use 
	create_path
	'''
	if ' ' in name or len(name) == 0: return False
	cmd = smb + ['"mkdir ' + name +'"']
	print('executing command:',' '.join(cmd))
	name = make_name()
	os.system(' '.join(cmd) + catch_output(name))
	out = get_output(name)
	if verbose: print(out)
	return out

def lsdir(path = '', verbose = False) :
	'''Show the contents of the remote dir specified in path
	path 		a directory e.g. media/text
	verbose 	whether to show extra information
	'''
	if ' ' in path or len(path) == 0: cmd = smb + ['"ls"']
	else: cmd = smb + ['"cd ' + path+';ls"']
	if verbose:print('executing command:',' '.join(cmd))
	name = make_name()
	os.system(' '.join(cmd) + catch_output(name))
	out = get_output(name)
	if verbose:print(out)
	return out

def path2path_and_dir(path):
	'''extracts last directory and the preceding path
	path 		a directory e.g. media/text
	returns directory (text) path (media)
	'''
	if path == '': return '', ''
	p = path.split('/')
	if path.count('/') in [0,1]:
		if p[-1] != '':
			directory = p[-1] 
			path = p[-2] if len(p) > 1 else ''
		else: directory,path = p[-2], ''
	else:
		if p[-1] != '':
			directory,path = p[-1],'/'.join(p[:-1])
		else:
			directory,path = p[-2],'/'.join(p[:-2])
	return directory, path

def isdir(path, verbose = False):
	'''check whether the path exists in the remote folder (BACKUP)
	returns true if the path exists
	path 			a directory e.g. media/text
	verbose 		whether to show extra information
	'''
	directory, path = path2path_and_dir(path)
	directory += ' '
	out = lsdir(path,verbose)
	if verbose: print(directory,path)
	if directory in out:name_found = True
	try: is_directory = out.split(directory)[1].replace(' ','')[0] == 'D'
	except: is_directory = False
	return is_directory

def isfile(path, verbose = False):
	filename, path = path2path_and_dir(path)	
	filename += ' '
	out = lsdir(path,verbose)
	if verbose: print(filename,path)
	if filename in out:
		try: is_file= out.split(filename)[1].replace(' ','')[0] == 'A'
		except: is_file= False
	else: is_file = False
	return is_file

def mkdir(remote_path,verbose = False):
	'''Recursive function to create the directory/ies specified in the path.
	if all directories already exist does nothing	
	recursive function moves down the tree until a directory does not exists
	creates and moves up the tree
	Root directory is 'BACKUP' in the HOH-repositoryfiles werkgroepmap
	
	remote_path 		a directory e.g. media/text
	verbose 			whether to show extra information
	'''
	if isdir(remote_path): return 'path already exists'
	directory, path = path2path_and_dir(remote_path)
	if isdir(path,verbose) or path == '':
		if verbose: print('path exists',path,'making directory:' ,directory)
		name = path + '/' +directory if path != '' else directory
		_mkdir(name,verbose)
	else: 
		if verbose: print('path does not exists',path,directory)
		# create_path(path) this function used to be called create_path
		mkdir(path)
		if verbose: print('making directory',directory,'at',path)
		name = path + '/' +directory if path != '' else directory
		_mkdir(name,verbose)
	


def put_file(local_path, remote_path, filename):
	'''save a local file with smbclient to remote HOHrepositoryfiles
	local_path 		local directory were the file is located
	remote_path 	the remote directory were the file should be save
					if the directory does not exists it is created
	filename 		name of the file
	'''
	
	if not os.path.isdir(local_path): return 'ERROR local path does not exist'
	if not isdir(remote_path): mkdir(remote_path)
	local_name = local_path + filename
	remote_name = remote_path + filename
	cmd = smb + ['"put '+ local_name+ ' ' +remote_name+'"']
	print('executing command:',' '.join(cmd))
	out = os.system(' '.join(cmd))
	return out


