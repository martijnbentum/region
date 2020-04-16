import random
import string

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
	if id_type == 'letters':
		return ''.join(random.sample(string.ascii_letters*length,length))
	if id_type == 'numbers':
		return int(''.join(random.sample('123456789'*length,length)))
