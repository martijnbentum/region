from django.apps import apps
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from utils import view_util
from easyaudit.models import CRUDEvent

class Crud:
	def __init__(self,instance):
		i = instance
		self.instance = instance
		self.model_name = str(type(i)).split('.')[-1].split("'")[0].lower()
		self.app_name = str(type(i)).split('.')[0].split("'")[-1].lower()
		self.get_crud_events()

	def get_crud_events(self):
		events= CRUDEvent.objects.filter(
			content_type__model=self.model_name,object_id=self.instance.pk)
		self.events = [Event(e) for e in events]

	@property
	def contributers(self):
		return ' | '.join([e.user.username for e in self.events])

	@property
	def created(self):
		for e in self.events:
			if e.type == 'Create':
				return  e.username + ' ' + e.time_str
		return 'user unknown'

	def _make_change_fields_string(self, e):# changed_fields):
		if not e.changed: return ['no changes']
		o = []
		for k in e.cf_dict:
			old, new = e.cf_dict[k]
			o.append( k + ': ' + old + ' -> ' + new )
		return o


	@property
	def updates(self):
		return [e for e in self.events if e.type =='Update']


	@property
	def anychanges(self):
		return True if self.updates else False
		

	@property
	def updates_str(self):
		o = []
		for e in self.updates:
			cfs = self._make_change_fields_string(e)
			for cf in cfs:
				o.append(' | '.join([e.username,
					e.time_str,cf]))
		if o == []: return 'no updates'
		return o

	@property
	def last_update(self):
		if len(self.events) == 0: return 'unknown'
		e = self.events[0]
		if len(self.events) ==1 and e.type == 'Create':
			cf = 'created'
		else:
			cf = ' | '.join(self._make_change_fields_string(e))
		print(cf,9, len(self.events))
		return ' // '.join([e.time_str,e.username,cf])

	@property
	def last_update_time(self):
		if len(self.events) == 0: return 'time unknown'
		return self.events[0].time_str_exact
	
	@property
	def last_update_by(self):
		if len(self.events) == 0: return 'user unknown'
		return self.events[0].username

class Event:
	def __init__(self,e):
		self.event = e
		self.type = e.get_event_type_display()
		self.changed = True if e.changed_fields not in ['null',None] else False
		self.username = e.user.username
		self.set_time()
		if self.changed: self.set_changes()

	def set_changes(self):
		try: self.cf_dict = eval(self.event.changed_fields)
		except: raise ValueError('could not create dict from:',
			self.event.changed_fields)
		self.changes = [Change(self.username,self.time_str,k,self.cf_dict[k])
			for k in self.cf_dict.keys()]

	def set_time(self):
		e = self.event
		dt = e.datetime
		self.time_str_exact= dt.strftime('%d %B %Y %H:%M')
		self.time_str_day_short= dt.strftime('%d %B %Y')
		self.time_str_hour_short= dt.strftime('%H:%M')
		self.epoch = dt.timestamp()
		self.time_delta = dt.now().timestamp() - self.epoch
		temp = dt.now().strftime('%d %B %Y') == dt.strftime('%d %B %Y') 
		self.changed_today = temp
		temp = dt.now().strftime('%Y') == dt.strftime('%Y') 
		self.changed_thisyear = temp
		self.days_ago = round(self.time_delta / (24*3600))
		self.hours_ago = round(self.time_delta / 3600)
		self.minutes_ago = round(self.time_delta / 60)
		self.changed_recent= self.minutes_ago < 99
		if self.minutes_ago < 3: ts = 'a moment ago'
		elif self.changed_recent: ts = str(self.minutes_ago) + ' minutes ago'
		elif self.hours_ago < 6: ts = str(self.hours_ago) + ' hours ago'
		elif self.changed_today:ts = dt.strftime('today %H:%M') 
		elif self.days_ago < 2: ts = dt.strftime('yesterday %H:%M')
		elif self.days_ago < 6: ts = dt.strftime('last %A %H:%M')
		elif self.changed_thisyear: ts = dt.strftime('%d %B')
		else: ts = self.time_str_day_short
		self.time_str = ts

class Change:
	def __init__(self,user,time,field_name,state):
		self.username = user
		self.time = time
		self.field= field_name
		self.old_state = state[0]
		self.new_state = state[1]
		
		

def add_simple_model(request, name_space,model_name,app_name, page_name):
	modelform = view_util.get_modelform(name_space,model_name+'Form')
	form = modelform(request.POST)
	if request.method == 'POST':
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/catalogue/close/')
	model = apps.get_model(app_name,model_name)
	instances = model.objects.all().order_by('name')
	var = {'form':form, 'page_name':page_name, 'instances':instances}
	return render(request, 'persons/add_simple_model.html',var)


# Create your views here.
