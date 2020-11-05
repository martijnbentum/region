from django.apps import apps
from utilities.models import instance2names

exclude_apps = 'admin,auth,contenttypes,sessions,utilities,easyaudit'.split(',')
non_primary_apps = ['locations']

class Relations:
	'''finds all models that have a relation with this models.
	there are three types of relations:
		-a relation model (connecting this models with another models with potential other fields
		-a foreign key, a relation to another model
		-m2m, a relation to 1 one or more instances of another model
	these relation type are stored seperatly
	both the fields and model linked to those fields are stored 
	'''
	def __init__(self,model):
		self.app_name, self.model_name = instance2names(model)
		#retrieve all relation model ie model:Text -> TextPublication relation etc.
		self.relation_fields=[f for f in model._meta.get_fields() if f.one_to_many]
		self.relation_fields_str=[f.get_accessor_name() for f in self.relation_fields]
		self.relation_models = [f.related_model for f in self.relation_fields]
		#retrieve all foreign key fields and related models
		self.fk_fields = [f for f in model._meta.local_fields if f.is_relation]
		self.fk_fields_str= [f.get_cache_name() for f in self.fk_fields]
		self.fk_models = [f.related_model for f in self.fk_fields]
		#retrieve m2m fields and models
		self.m2m_fields = [f for f in model._meta.local_many_to_many if f.related_model != model]
		self.m2m_fields_str = [f.get_attname() for f in self.m2m_fields]
		self.m2m_models = [f.related_model for f in self.m2m_fields]

	def __repr__(self):
		m = 'relations of '
		m += 'app: '+self.app_name +' | '
		m += 'model: '+self.model_name 
		return m

	def __str__(self):
		m = 'app: '+self.app_name +'\n'
		m += 'model: '+self.model_name +'\n'
		m += 'relation models:\n\t' + model_list2str(self.relation_models,'\n\t') + '\n\n'
		m += 'fk models:\n\t' + model_list2str(self.fk_models,'\n\t') + '\n\n'
		m += 'm2m models:\n\t' + model_list2str(self.m2m_models, '\n\t')+'\n\n'
		return m

class Connection_set:
	'''collect all connections for one or more instances.
	can also recursively collect all connections for one or more instances
	i.e. find all connections for instances connected to the original set of instances
	'''
	def __init__(self):
		self.pk = Pk()
		self.connections = []
		self.input_instances = []
		self.counter = 0

	def __repr__(self):
		return 'connections for ' + str(len(self.input_instances)) + ' instances'

	def __str__(self):
		m = self.__repr__()
		return m + self.pk.__str__()

	def add_instances(self,instances, recursive = False):
		for instance in instances:
			if hasattr(instance,'endnode'):
				self.input_instances.append(instance)
				continue
			self.add_instance(instance)
		if recursive: self._run_recursive()

	def add_instance(self, instance, recursive = False):
		self.input_instances.append(instance)
		c = Connections(instance)
		self.pk.update(c.pk)
		self.connections.append(c)
		if recursive: self._run_recursive()

	def _run_recursive(self):
		self.counter += 1
		dif = list(set(self.instances) - set(self.input_instances))
		print('finding connections recursively, order:',self.counter,'instances:',len(dif))
		if dif: self.add_instances(dif,True)
		
			
			

	@property
	def instances(self):
		return self.pk.instances


class Connections:
	'''find all pk, app_name and model name of all connected instances of a given instance.'''
	def __init__(self,instance):
		self.instance = instance
		self.app_name, self.model_name = instance2names(instance)
		self.name = self.app_name + ' ' + self.model_name
		#retrieve all relation model ie model:Text -> TextPublication relation etc.
		self.relations = Relations(instance)
		self.pk = Pk()
		self.pk.add_instance(instance)
		for f in self.relations.relation_fields_str + self.relations.m2m_fields_str:
			rm = getattr(instance,f)
			self.pk.add_qeuryset(rm.all())
		for f in self.relations.fk_fields_str:
			ri = getattr(instance,f)
			self.pk.add_instance(ri)


	def __repr__(self):
		return 'connections for ' + self.name +' : '+ str(self.instance)

	def __str__(self):
		m = self.__repr__()
		return m + '\n' + str(self.pk)

	@property
	def instances(self):
		return self.pk.instances


class Pk:
	'''contain all pk for the different apps and models'''
	def __init__(self):
		self.d = {}
		self.d_newly_added = {}
		self.newly_added = True
		self._instances = []

	def add_instance(self,instance):
		if not instance:return
		k = instance2names(instance)
		if k not in self.d: self.d[k] = []
		if k not in self.d_newly_added: self.d_newly_added[k] = []
		if instance.pk not in self.d[k]: 
			self.newly_added = True
			self.d[k].append( instance.pk ) 
			self.d_newly_added[k].append( instance.pk)

	def add_qeuryset(self,qs):
		for instance in qs:
			self.add_instance(instance)

	def __repr__(self):
		lines = [', '.join(line) for line in self.d.keys()]
		values = [', '.join(map(str,self.d[key])) for key in self.d.keys()]
		longest = getlongeststr(lines) + 3
		m = '\n'.join([l.ljust(longest) + v for l, v in zip(lines,values)])
		return m

	def __str__(self):
		return self.__repr__()
		

	def update(self,other):
		for k in other.d:
			if k not in self.d: self.d[k] = []
			if k not in self.d_newly_added: self.d_newly_added[k] = []
			for value in other.d[k]:
				if value not in self.d[k]:
					self.newly_added = True
					self.d[k].append(value)
					self.d_newly_added[k].append(value)
				
	@property
	def instances(self):
		if self.newly_added:
			for k in self.d_newly_added.keys():
				model = apps.get_model(*k)
				for pk in self.d_newly_added[k]:
					self._instances.append(model.objects.get(pk =pk))
			self.newly_added = False
			self.d_newly_added = {}
		return self._instances
		
	
def model_list2str(ml,sep = '\t'):
	return sep.join([str(m) for m in ml]) 
		
def queryset2pk(qs):	
	return [i.pk for i in qs]
	
def getlongeststr(lines):
	longest = 0
	for line in lines:
		if len(line) > longest: longest = len(line)
	return longest
