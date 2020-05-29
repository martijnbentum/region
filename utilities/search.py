from django.apps import apps
from django.db.models.functions import Lower
from django.db.models import Q

class Search:
	'''search a django model on all fields or a subset with Q objects'''
	def __init__(self,request, model_name='',app_name=''):
		'''search object to filter django models
		query 				search terms provided by user
		search_fields 		field set to restrict search (obsolete?)
		model_name 			name of the django model
		app_name 			name of the app of the model
		'''
		self.request = request
		self.query = Query(request,model_name)
		self.order = self.query.order
		self.model_name = model_name
		self.app_name = app_name
		self.model = apps.get_model(app_name,model_name)
		self.fields = get_fields(model_name,app_name)
		self.select_fields()
		self.notes = 'Search Fields: (' + ','.join([f.name for f in self.fields if f.include]) + ')'

	def select_fields(self):
		if self.query.fields:
			for field in self.fields:
				if field.name in self.query.fields: field.include = True
				else: field.include = False

	def check_and_or(self, and_or):
		if and_or == '': 
			self.and_or = 'and' if 'and' in self.query.special_terms else 'or'
		if self.and_or == 'and': self.notes += '\nall fields should match query'
		else: self.notes += '\none ore more fields should match query'

	def check_combine(self, combine):
		self.combine = self.query.combine if combine == None else combine
		if self.combine:
			self.notes += '\ncombined query term: ' + self.query.clean_query
		else: self.notes += '\nseperate query terms: ' + ', '.join(self.query.query_terms)

	def check_completeness_approval(self):
		if self.query.completeness != None: 
			self.result = self.result.filter(complete=self.query.completeness)
			self.notes += '\ncompleteness: ' + str(self.query.completeness)
		if self.query.approval != None: 
			self.result = self.result.filter(approved=self.query.approval)
			self.notes += '\napproval: ' + str(self.query.approval)

	def set_ordering_and_direction(self):
		self.result = self.result.order_by(Lower(self.order.order_by))
		self.notes += '\nordered on field: ' + self.order.order_by
		if self.order.direction == 'descending': 
			self.result= self.result.reverse()
		self.notes += '\nordered in ' + self.order.direction + ' order'

	def filter(self, option = 'icontains',and_or='',combine= None):
		'''method to create q objects and filter instance from the database
		option 		search term for filtering, default capital insensitive search
		and_or 		whether q objects have an and/or relation
		seperate 	whether the words in the query should be searched seperately or not
		'''
		self.check_and_or(and_or)
		self.check_combine(combine)
		self.qs = []
		for field in self.fields:
			if field.include: 
				if self.combine:
					term = self.query.clean_query
					self.qs.append(field.create_q(term=term,option=option))
				else:	
					for term in self.query.query_terms:
						self.qs.append(field.create_q(term=term,option=option))
		self.q = Q()
		for qobject in self.qs:
			if self.and_or == 'and': self.q &= qobject
			else: self.q |= qobject
			
		self.result = self.model.objects.filter(self.q)
		self.check_completeness_approval()
		self.set_ordering_and_direction()
		return self.result

	@property
	def n(self):
		print(self.notes)



class Query:
	'''class to parse a http request extract query and extract relevant information.'''
	def __init__(self,request, model_name=''):
		'''individual words and special terms are extracted from the query.
		a clean version of the query (without special terms) is constructed.
		$ 	symbol prepended to field names
		* 	symbol prepended to special terms such as and/or
		'''
		self.order = Order(request,model_name)
		self.query = self.order.query
		self.query_words = self.query.split(' ')
		self.words = self.query_words
		self.query_terms = [w for w in self.words if w and w[0] not in ['*','$']]
		self.clean_query = ' '.join(self.query_terms)
		self.extract_field_names()
		self.extract_special_terms()

	def extract_field_names(self):
		temp= [w[1:] for w in self.words if len(w) > 1 and w[0] == '$']
		self.field_term, self.fields= [],[]
		for term in temp:
			if ':' in term:self.field_term.append(term.split(':'))
			else: self.fields.append(term.lower())

	def extract_special_terms(self):
		self.special_terms = [w[1:].lower() for w in self.words if len(w) > 1 and w[0] == '*']
		if 'complete' in self.special_terms: self.completeness = True
		elif 'incomplete' in self.special_terms: self.completeness = False
		else: self.completeness = None
		if 'approved' in self.special_terms: self.approval = True
		elif 'unapproved' in self.special_terms: self.approval = False
		else: self.approval = None
		self.combine = 'True' if 'combine' in self.special_terms else False
			
	
			
class Field:
	def __init__(self,name,description):
		self.name = name
		self.description = description
		self.set_field_type()
		self.check_relation()
		self.set_include()

	def __repr__(self):
		return self.name

	def set_include(self, value = None):
		self.include = True 
		if self.name == 'id' or self.bool or self.file or self.image: self.include = False 
		if value != None and value in [True,False]: self.include = value


	def set_field_type(self):
		'''sets booleans for field types (see field_typedict).'''
		ftd = get_field_typesdict()
		for name in ftd.keys():
			v= True if name in self.description else False
			setattr(self,ftd[name],v)

	def check_relation(self):
		'''checks whether a field is a foreign key or m2m and creates the full name
		variable to end up with a field to be filtered on (whether it is a relational
		field or not.'''
		self.relation = True if self.fk or self.m2m else False
		fkd = get_foreign_keydict()
		if self.relation:
			if self.name in fkd.keys(): 
				self.related_name = fkd[self.name]
				self.full_name = self.name +'__' + self.related_name
			else: 
				print('could not find related name of relational field',
					self.name,self.description)
				self.include =False
		else: self.full_name = self.name

	def create_q(self, term, option='icontains'):
		'''creates django q object for filtering'''
		self.q = Q(**{'__'.join([self.full_name,option]):term})
		return self.q
		

class Order:
	def __init__(self,request, model_name):
		self.request = request
		self.model_name = model_name

		temp = request.GET.get('order_by')
		tquery = request.GET.get('query')
		if temp: 
			order_by,old_order,old_direction,tquery = temp.split(',')
			if order_by == old_order:
				direction = 'descending' if old_direction == 'ascending' else 'ascending'
			else: direction = 'ascending'
		else: 
			order_by = get_foreign_keydict()[self.model_name.lower()]
			direction = 'ascending'
			
		if tquery == None: query = ''
		else: query =tquery

		self.order_by = order_by
		self.query = query
		self.direction = direction

	def __repr__(self):
		return self.order_by + ', ' + self.direction


def get_fields(model_name,app_name):
	'''Get field names from a model (for now ignore many to one relations. 
	For example persontextrelation field is ignored on Text.
	'''
	model = apps.get_model(app_name,model_name)
	o = []
	for f in model._meta.get_fields():
		if hasattr(f,'description'): # skips ManyToOneRel
			o.append(Field(f.name,f.description))
	return o


def make_dict(s):
	return dict([i.split(':') for i in s.split(',')])

def get_field_typesdict():
	m = 'Foreign Key:fk,Many-to-many:m2m,Boolean:bool,Integer:int,String:str'
	m += ',File:file,Image:image,PartialDateField:partial_date'
	return make_dict(m)
	

def get_foreign_keydict():
	m = 'publication:title,text:title,illustration:caption,publisher:name,location:name'
	m += ',person:first_name,movement:name,periodical:title,language:name,genre:name'
	m+= ',category:name,movement_type:name,form:name'
	return make_dict(m)


'''
	publications = Publication.objects.filter(
		Q(title__icontains=query) | eval('Q(form__name__icontains=query)') |
		Q(publisher__name__icontains=query) | Q(location__name__icontains=query)).order_by(Lower(order_by))
'''
