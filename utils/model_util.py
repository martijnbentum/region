import random
import string
import itertools

class info():
	'''inherit from this class to add extra viewing functionality for models'''

	HEADER = '\033[95m'
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	END = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

	def view(self):
		'''show all attributes of instance'''
		print(self.UNDERLINE,self.__class__,self.END)
		n = max([len(k) for k in self.__dict__.keys()]) + 3
		for k in self.__dict__.keys():
			print(k.ljust(n),self.BLUE,self.__dict__[k], self.END)

	@property
	def info(self):
		n = max([len(k) for k in self.__dict__.keys()]) + 3
		m = '<table class="table table-borderless" >'
		for k in self.__dict__.keys():
			if k == '_state' or k == 'id': continue
			m += '<tr class="d-flex">'
			m += '<th class="col-2">'+k.ljust(n)+'</th>'
			m += '<td class="col-8">'+str(self.__dict__[k]) +'</td>'
		m += '</table>'
		return m

	


def id_generator(id_type= 'letters', length = 9):
	'''probably obsolete, generate a random identifier string for an isntance.'''
	if id_type == 'letters':
		return ''.join(random.sample(string.ascii_letters*length,length))
	if id_type == 'numbers':
		return int(''.join(random.sample('123456789'*length,length)))


def compare_dicts(sd,od):
	'''Compare model class dictionary to compare the similarity of two model instances.
	helper function of compare_instances
	'''
	equal,similar = True, True
	ntotal,nsame,nsimilar = len(sd.keys())-2, 0, 0
	for k in sd.keys():
		if k in ['id','_state']:continue # skip fields that are different by definition
		if sd[k] == od[k]: 
			nsame +=1
			nsimilar +=1
		elif sd[k] in ['',None] or od[k] in ['',None]: 
			equal = False
			nsimilar +=1
		else: 
			equal,similar = False,False
	perc_same,perc_similar = nsame/ntotal,nsimilar/ntotal
	return equal,perc_same,similar,perc_similar

def compare_instances(self,other):
	'''Compare two instances.
	If each field for the two instances are identical returns equal true

	If fields for the instances only differs  whereby one has default empty value (i.e. none or '')
	return similar true

	Also returns percentage for both equal and similar
	'''
	if type(self) != type(other):
		print(self,'is not of the same type as:',other,type(self),type(other))
		return False,0,False,0
	sd, od = self.__dict__, other.__dict__
	return compare_model_dicts(sd,od)

def compare_queryset(qs):
	'''Compare all unordered paired combinations of instances in a queryset a
	determines the equality / similarity of the pair. (see compare_ instances)
	'''
	equal_list,similar_list,complete_list = [],[],[]
	for a,b in itertools.combinations(qs,2): #create all unordered paired combinations in the qs
		equal,pe,similar,ps = compare_instances(a,b)
		line = [a,b,equal,pe,similar,ps]
		if equal: equal_list.append(line)
		if similar: similar_list.append(line)
		complete_list.append(line)
	return equal_list, similar_list, complete_list
		
	
		
		
