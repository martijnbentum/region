from utilities.models import GroupTag
from utils.model_util import id_generator
from .export import Relations

class GroupTags:
	'''Group GroupTag object together and sort them on index creation or modification time.'''
	def __init__(self,name ='',tag_type = None, filter_out_done =True): 
		'''Create an instance to group GroupTag objects an iterate over them.
		name 				name of the GroupTag
		tag_type 			tag type of the GroupTag
		filter_out_done 	whether to exclude finished tags
		'''
		self.name = name
		self.tag_type = tag_type
		self.filter_out_done = filter_out_done
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
		'''Create a dictionary mapping GroupTag objects 2 corresponding instance.
		if a GroupTag is marked as done and filter_out_done flag is set the GroupTag is skipped
		if a GroupTag is not connected to an object it is skipped
		'''
		self.tag2instance_dict = {}
		for tag in self.tags:
			if self.filter_out_done and tag.done: continue
			instance = tag2instance(tag)
			if instance: self.tag2instance_dict[tag] = instance


	def sort_index(self,reverse=False):
		'''Sort on the index, if this is no specified for one or more GroupTag objects
		creation time is used.'''
		self.index_available= sum([type(x.index) == int for x in self.tags]) == len(self.tags)
		if self.index_available: self.tags.sort(key=lambda x: x.index, reverse=reverse)
			
		else: 
			print('WARNING, no index available for all group tags, using creation time instead')
			self.sort_time_created(reverse)

	def sort_time_created(self,reverse=False):
		'''Sort on creation time, this is default because it is garanteed to exists.'''
		self.tags.sort(key=lambda x: x.created, reverse=reverse)

	def sort_time_modified(self,reverse=False):
		'''Sort on modification time, if this is no specified for one or more GroupTag objects
		creation time is used.'''
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
		'''List all existing GroupTag names.'''
		all_tag_names()

	def all_tag_types(self):
		'''List all existing GroupTag tag types.'''
		all_tag_types()


class MakeGroupTags:
	'''Create GroupTag objects to group a set of instances.'''
	def __init__(self,name ='',tag_type = None, description = None, enforce_unique_name= True): 
		'''Create GroupTag objects to group a set of instances.
		name 					GroupTag name
		tag_type 				GroupTag tag type
		description 			description of the GroupTag
		enforce_unique_name 	whether the GroupTag name can already exists
								if the name exists the instances are added to an existing group 
		'''
		if enforce_unique_name: self.name = make_unique_name(name)
		else: self.name = name
		self.tag_type = tag_type
		self.description = description
		self.tags = list(GroupTag.objects.filter(name = name))
		self.instances = [tag2instance(tag) for tag in self.tags]


	def add_grouptag(self,goal_instance,tag_type = None,index= None,description =None):
		'''Create GroupTag and connect it to the goal_instance.'''
		if not description: description = self.description
		gt = GroupTag(name = self.name,tag_type= self.tag_type,index= index, description= description)
		gt.save()
		goal_instance.group_tags.add(gt)
		self.tags.append(gt)
		self.instances.append(goal_instance)

	def add_grouptags(self,goal_instances,tag_type = None,set_index = False,index_start=0,
		description =None):
		'''For each instance in goal_instances, create a GroupTag and connect it to the goal_instance.
		goal_instances 		list of instance to connect a tag to
		tag_type 			name of the tag type (alternative grouping handle), default None
		set_index 			whether to set the index on the tags, default False
		index_start 		start the index at the specified integer, default = 0
		description 		a description of the GroupTag, default None
		'''
		i = index_start if set_index else None
		for instance in goal_instances:
			self.add_grouptag(goal_instance=instance,tag_type=tag_type,
				index =i, description=description)
			if set_index: i += 1


def make_unique_name(name= ''):
	'''Create a GroupTag name that does not exist.
	name 		optional name that will be prepended to letter string to make it unique
				if necessary 
	'''
	if not name: name = id_generator(length = 5)
	names = list(set([x.name for x in GroupTag.objects.all()]))
	if name not in names:
		return name
	else: return self.make_unique_name(name + '_' + id_generator(length = 2))


def tag2instance(tag,verbose = False):
	'''Get the instance connected to the GroupTag.
	assumes only one object is linked to the GroupTag.
	'''
	r = Relations(tag)
	for field_name in r.reverse_m2m_fields_str:
		queryset= getattr(tag,field_name).all()
		if queryset.count(): return queryset[0]
	if verbose: print('unconnected tag, no instance found')
	return None

def all_tag_names():
	'''List all existing GroupTag names.'''
	return list(set([x.name for x in GroupTag.objects.all()]))

def all_tag_types():
	'''List all existing GroupTag tag types.'''
	return list(set([x.tag_type for x in GroupTag.objects.all()]))
