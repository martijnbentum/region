def flatten_lol(lol):
	'''flattens a list of lists.'''
	return [item for sublist in lol for item in sublist]


def sort_count_dict(d, remove_empty = True):
	temp = []
	for key, val in d.items():
		if remove_empty and val == 0: continue
		temp.append([key,val])
	temp = sorted(temp, key=lambda x: x[1],reverse = True)
	d = dict(temp)
	return d

def count_dict_to_percentage_dict(d,sort=True,remove_empty=True):
	total = sum(d.values())
	temp = []
	if sort: d = sort_count_dict(d,remove_empty=remove_empty)
	for key, val in d.items():
		if remove_empty and val == 0: continue
		temp.append([key, round(val /total * 100,2)])
	d = dict(temp)
	return d

def sort_dict_on_keys(d) :
	temp = []
	for key, value in d.items():
		temp.append([key,value])
	temp = sorted(temp, key = lambda x: x[0], reverse = False)
	d = dict(temp)
	return d
		
def remove_keys_from_dict(d,keys):
	for key in keys:
		if not key in d.keys(): continue
		del d[key]
