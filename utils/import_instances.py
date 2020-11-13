import copy
from django.apps import apps
from utilities.models import instance2names
from django.core import serializers
from openpyxl import Workbook
from openpyxl import load_workbook
from .model_util import compare_instances
from .export import format_dict
from partial_date.partial_date import PartialDate


class Import:
	'''Import instances from an excel file
	each sheet contains instances for a specific model
	the excel file should be created with the export function
	'''
	def __init__(self,filename):
		'''filename 	filename of the excel file'''
		self.filename = filename
		self.wb = load_workbook(filename)
		self.fieldtypes = self.wb['fieldtypes']
		self.amn = list(set([l[:2] for l in list(self.fieldtypes.values)[1:]]))
		self.app_names,self.model_names = [i for i,j in self.amn],[j for i,j in self.amn]
		self.models = [apps.get_model(*mn) for mn in self.amn]
		self.create_column_dicts() 
		self.names2model = dict([[name,model] for name,model in zip(self.model_names,self.models)])
		self.import_instances = {}
		self.all_import_instances = []

	def __repr__(self):
		m = 'import file: '+self.filename+' models: '
		m += str(len(self.import_instances))
		m += ' instances: ' + str(len(self.all_import_instances))
		return m

	def __str__(self):
		m = self.__repr__() + '\n'
		m += format_dict(self.import_instances)
		return m

	def create_column_dicts(self):
		'''a dict of dicts, model name maps to a dictionary, this dictonary contains column
		names and fieldtype and fk/m2m model names.'''
		self.column_dicts = {}
		for model_name in self.model_names:
			d = {}
			for line in self.fieldtypes.values:
				if model_name == line[1]:
					d[line[2]]=line[3:]
			self.column_dicts[model_name] = d
				
	def make_instances(self):
		'''create instances for all rows for all sheets in the excel file.'''
		self.import_instances = {}
		self.complete, self.incomplete = [], []
		self.pk_not_in_db_instances = []
		self.equal_instances,self.similar_instances, self.mismatch_instances = [], [], []
		for model_name in self.model_names:
			sheet = self.wb[model_name]
			cd = self.column_dicts[model_name]
			ii = ImportInstances(sheet,cd,model_name,self.names2model)
			ii.make_instances()
			self.import_instances[model_name] = ii
			self.complete.extend(ii.complete)
			self.incomplete.extend(ii.incomplete)
			self.pk_not_in_db_instances.extend(ii.pk_not_in_db_instances)
			self.equal_instances.extend(ii.equal_instances)
			self.similar_instances.extend(ii.similar_instances)
			self.mismatch_instances.extend(ii.mismatch_instances)
			self.all_import_instances.extend(ii.import_instances)
		
class ImportInstances:
	'''Collects all instances of a specific model based on exported excel sheet
	the excel sheet should be created with Export function and contain instances of 
	as specific model.
	'''
	def __init__(self,sheet,column_dict,model_name,names2model):
		'''sheet 		excel sheet with information for an instance on each row
		column dict 	a dictionary that contains the name of each column and
						field type and optionally the related model (e.g. foreign key field)
		model_name 		name of the model
		names2model 	dictionary translating model names to the actual model
		'''
		self.sheet = sheet
		self.column_dict = column_dict
		self.model = names2model[model_name]
		self.model_name = model_name
		self.names2model = names2model
		self.sheet_values= list(sheet.values)
		self.column_names = self.sheet_values[0]
		self.coln2i = dict([[name,i] for i,name in enumerate(self.column_names)])
		self.import_instances = []
	
	def __repr__(self):
		m = 'import instances: ' + self.model_name + ' loaded: '
		m += str(len(self.import_instances))
		return m

	def __str__(self):
		m = self.__repr__()
		return m
		

	def make_instances(self):
		'''create ImportInstances that create an instance based on a row in the excel sheet'''
		self.import_instances, self.pk_not_in_db_instances = [], []
		self.equal_instances,self.similar_instances, self.mismatch_instances = [], [], []
		self.complete, self.incomplete= [],[]
		for row in self.sheet_values[1:]:
			ii = ImportInstance(row,self.coln2i,self.column_dict,self.model,self.names2model)
			ii.make_instance()
			self.import_instances.append(ii)
			if not ii.db_instance: self.pk_not_in_db_instances.append(ii)
			elif ii.equal: self.equal_instances.append(ii)
			elif ii.similar: self.similar_instances.append(ii)
			else: self.mismatch_instances.append(ii)

			if ii.all_related_instance_present: self.complete.append(ii)
			else: self.incomplete.append(ii)

	@property
	def instances(self):
		if not hasattr(self,'import_instances'):self.make_instances()
		return [i.instance for i in self.import_instances]

			

class ImportInstance:
	'''import instance for a single row in an excel sheet corresponding to instance
	of a specific model.'''
	def __init__(self,row,coln2i,column_dict,model,names2model):
		self.original_row = row
		self.coln2i = coln2i
		self.column_dict = column_dict
		self.model = model
		self.names2model = names2model
		self.app_name, self.model_name = instance2names(model) 
		self._set_row_values()

	def __repr__(self):
		if hasattr(self,'instance'):
			m = self.instance.__repr__()
			m += ' complete: '+str(self.complete) + 'equal: ' + str(self.equal)
			m += 'in db: ' + str(self.db_instance)

	def _set_row_values(self):
		'''transform the values in the excel sheet to the correct data type.
		e.g. str -> bool for boolean fields
		number fields are not transformed since they can handle str data
		'''
		self.row = list(copy.copy(self.original_row))
		for column_name in self.column_dict.keys():
			ctype = self.column_dict[column_name][0]
			i = self.coln2i[column_name]
			val = self.row[i]
			if ctype == 'BooleanField':
				if val == 'False':self.row[i] = False
				if val == 'True':self.row[i] = True
			if ctype == 'DateTimeField' and val:
				self.row[i] = PartialDate(val)

	def get_values(self):
		'''collect the data into an dictionary of column name: value
		values are already transformed with the _set_row_value method'''
		self.values = {}
		self.relational_fields = {}
		self.non_relational_fields = {}
		for key in self.coln2i.keys():
			index = self.coln2i[key]
			self.values[key] = self.row[index]
			if key == 'pk': continue
			if self.row[index] == None: continue
			if self.column_dict[key][1]:
				self.relational_fields[key] = self.row[index]
			else: self.non_relational_fields[key] = self.row[index]
		self.collect_relations()

	def collect_relations(self):
		'''collect instances of relation fields (foreign keys /many to many relations).
		collected in a dictionary of column name: instance
		only if the column contains a value
		'''
		self.related_instance={}
		self.all_related_instance_present = True
		for key,pk in self.relational_fields.items():
			relation_type, related_model_name = self.column_dict[key]
			related_model = self.names2model[related_model_name]
			pk = self.relational_fields[key]
			if not pk: continue
			self._add_related_instance(pk,relation_type,related_model,key)

	def _add_related_instance(self,pk,relation_type,related_model,key):
		'''adds the related instance to the related_instance dictionary.'''
		if relation_type == 'ManyToManyRel':
			self.related_instance[key] = []
			pks = pk.split(';')
			for pk in pks:
				self.related_instance[key].append(self._get_related_instance(related_model,pk))
		else:
			self.related_instance[key] = self._get_related_instance(related_model,pk)

	def _get_related_instance(self,related_model,pk):
		'''check whether an related instance is present and returns it from the database.
		if related instance is not present it returns the pk and set the related instance present
		flag to false.
		'''
		try: return related_model.objects.get(pk=pk)
		except: 
			self.all_related_instance_present =False
			return pk

	def make_instance(self):
		'''create an instance based on the excel row.
		checks whether an instance with the same pk is in the database
		checks whether the db instance is equal or similar to the created instance
		similar is the case when only fields differ if they are empty or not
		'''
		if not hasattr(self,'values'):self.get_values()
		try:self.db_instance = self.model.objects.get(pk = self.values['pk'])
		except:self.db_instance = False	
		self.instance = self.model(**self.non_relational_fields)
		self.instance.pk = self.values['pk']
		i,dbi = self.instance, self.db_instance
		self.equal,self.perc_same,self.similar,self.perc_similar = compare_instances(i,dbi)
