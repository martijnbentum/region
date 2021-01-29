from utilities.models import GroupTag
from utils.model_util import id_generator
from .export import Relations

class GroupTags:
	def __init__(self,name ='',tag_type = None, filter_out_done =True): 
		self.name = name
		self.tag_type = tag_type
		kwargs = {}
		if name: kwargs.update({'name':name})
		if tag_type: kwargs.update({'tag_type':tag_type})

		if name == 'all_grouptags' or kwargs == {}:self.tags= list(GroupTag.objects.all())
		else: self.tags = list(GroupTag.objects.filter(**kwargs))
		self._make_tag_instance_dict()


	def __repr__(self):
		if not self.name: return 'no grouptag set selected'
		return 'grouptag set of: '+self.name+ ' with: ' + str(len(self.tags)) + ' tags'

	def __getitem__(self,index):
		return self.tags[index]


	def _make_tag_instance_dict(self):
		self.tag2instance_dict = {}
		for tag in self.tags:
			instance = tag2instance(tag)
			self.tag2instance_dict[tag] = instance


	def sort_index(self,reverse=False):
		self.index_available= sum([type(x.index) == int for x in self.tags]) == len(self.tags)
		if self.index_available: self.tags.sort(key=lambda x: x.index, reverse=reverse)
			
		else: 
			print('WARNING, no index available for all group tags, using creation time instead')
			self.sort_time_created(reverse)

	def sort_time_created(self,reverse=False):
		self.tags.sort(key=lambda x: x.created, reverse=reverse)

	def sort_time_modified(self,reverse=False):
		self.modified_available = None not in [x.modified for x in self.tags]
		if self.modified_available: self.tags.sort(key=lambda x: x.modified, reverse=reverse)
		else: 
			print('''WARNING, no modified time stamp available for all group tags, 
				using creation time instead''')
			self.sort_time_created(reverse)


	def view(self):
		for x in self.tags:
			x.view()

	def all_tag_names(self):
		return list(set([x.name for x in GroupTag.objects.all()]))

	def all_tag_types(self):
		return list(set([x.tag_type for x in GroupTag.objects.all()]))

class MakeGroupTags:
	def __init__(self,name ='',tag_type = None, description = None, enforce_unique_name= True): 
		if enforce_unique_name: self.name = make_unique_name(name)
		else: self.name = name
		self.tag_type = tag_type
		self.description = description
		self.tags = list(GroupTag.objects.filter(name = name))


	def add_grouptag(goal_instance,tag_type = None,index= None,description =None):
		if not name: name = make_unique_name()
		if not tag_type: tag_type = tag_type = self.tag_type
		if not description: description = self.description
		gt = GroupTag(name = name,tag_type= tag_type,index= index, description= description)
		goal_instance.group_tags.add(gt)
		self.tags.append(gt)
		


def make_unique_name(name= ''):
	if not name: name = id_generator(length = 5)
	names = list(set([x.name for x in GroupTag.objects.all()]))
	if name not in names:
		return name
	else: return self.make_unique_name(name + '_' + id_generator(length = 2))

def tag2instance(tag,verbose = False):
	r = Relations(tag)
	for field_name in r.reverse_m2m_fields_str:
		queryset= getattr(tag,field_name).all()
		if queryset.count(): return queryset[0]
	if verbose: print('unconnected tag, no instance found')
	return None
