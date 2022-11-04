from django.apps import apps
import inspect
import sys
from easyaudit.models import CRUDEvent
from utils import signal_util
from .model_util import instance2name, instance2names

def get_modelform(namespace,modelform_name):
    temp = sys.modules[namespace]
    classes = dict(inspect.getmembers(temp,inspect.isclass))
    try: return classes[modelform_name]
    except: 
        raise ValueError(
            'could not find',modelform_name,'in',classes,'did you import it?')


def _wip_edit_model(request, instance_id, app_name, model_name):
    #WORK IN PROGRESS: should get modelform or import all model forms
    '''edit view generalized over models.
    assumes a 'add_{{model_name}}.html template and edit_{{model_name}} function
    and {{model_name}}Form
    '''
    model = apps.get_model(app_name,model_name)
    modelform = get_modelform(__name__,model_name+'Form')
    instance= model.objects.get(pk=instance_id)
    if request.method == 'POST':
        form = modelform(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse(app_name+':edit_'+model_name.lower(), 
                args = [instance.pk]))
    form = modelform(instance=instance)
    args = {'form':form,'page_name':'Edit '+model_name.lower()}
    return render(request,app_name+'/add_' + model_name.lower() + '.html',args)


class FormsetFactoryManager:
    '''object that hold formset factories and corresponding names.
    use case: and add/edit view uses many formsets these can be created
    with this class by providing a list of names of the formset factory functions
    the formsets are stored in formset variable and the dict variable contains
    a name / formset to update the var variable provided for the template
    (names can be used in the template to acces the formsets)
    '''
    def __init__(self,name_space,names,request=None,instance=None):
        '''
        names_sp    __name__
        names       csv or list of names, should correspond to formset factories 
                    imported in the module calling this class
        request     django request variable
        instance    instance of model that is updated
        ''' 
        self.names = names.split(',') if type(names) == str else names
        self.formset_factories = [get_modelform(name_space,name)
             for name in self.names if name != '']
        if request == None:
            self.formsets = [ff(instance=instance) for ff in self.formset_factories]
        else:
            self.formsets = [ff(request.POST, request.FILES,instance=instance) 
                for ff in self.formset_factories]
        self.dict = dict([[name,fs] for name,fs in zip(self.names,self.formsets)])

    def __repr__(self):
        return ' '.join(self.names)
        
    def save(self):
        self.valid,self.errors = True,[]
        for formset in self.formsets:
            if formset.is_valid(): formset.save()
            else: 
                self.valid = False
                self.errors.append(formset.errors)
        return self.valid


class Cruds:
    def __init__(self,app_name,model_name, related_name = ''):
        self.app_name = app_name
        self.model_name = model_name
        self.model = apps.get_model(app_name,model_name)
        self.instances = self.model.objects.all()
        self.cruds = [Crud(i) for i in self.instances]
        self.cruds.sort(reverse = True)

    def __repr__(self):
        return ' '.join([self.app_name,self.model_name,'n:',str(self.ninstances)])

    @property
    def ninstances(self):
        return len(self.cruds)

    @property
    def last_update(self):
        return self.cruds[0].last_update
        

class Crud:
    def __init__(self,instance,related_name = '',add_related_events = True, user= False):
        i = instance
        self.instance = instance
        self.related_name = related_name
        self.add_related_events = add_related_events
        self.user = user
        self.model_name = str(type(i)).split('.')[-1].split("'")[0].lower()
        self.app_name = str(type(i)).split('.')[0].split("'")[-1].lower()
        if user: self.get_user_crud_events()
        else: self.get_crud_events()
        if add_related_events: self._add_related_events()

    def get_user_crud_events(self):
        events= CRUDEvent.objects.filter(
            user__username=self.instance.username)
        self._get_crud_events(events)

    def get_crud_events(self):
        events= CRUDEvent.objects.filter(
            content_type__model=self.model_name,object_id=self.instance.pk)
        self._get_crud_events(events)

    def _get_crud_events(self,events):
        o = []
        for e in events:
            if self.user: o.append(e)
            elif e.get_event_type_display() == 'Create':o.append(e)
            elif not e.changed_fields: e.delete() 
            else: o.append(e) #store 
        self.events = [Event(e,self.related_name,self.instance) for e in o]

    def _add_related_events(self):
        self.cruds = []
        for attr in dir(self.instance):
            if 'relation_set' in attr and not attr.startswith('_'):
                cruds = [Crud(ri,instance2name(ri),False) for ri in 
                    getattr(self.instance,attr).all()]
                self.cruds.extend(cruds)
            if attr == 'relations':
                for r in self.instance.relations.through.objects.all():  
                    if hasattr(r,'primary'): pk1,pk2 = r.primary.pk,r.secondary.pk
                    elif hasattr(r,'container'):pk1,pk2=r.container.pk,r.contained.pk
                    else: continue
                    if self.instance.pk in [ pk1, pk2 ]:
                        self.cruds.append(Crud(r,instance2name(r)))

    def __lt__(self,other):
        if len(self.events) == 0: return True
        if len(other.events) == 0: return False
        return self.events[0].epoch < other.events[0].epoch

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return ' // '.join([self.app_name,self.model_name, self.last_update])

    @property
    def contributers(self):
        return ', '.join(list(set([u.username for u in self.updates if u.username])))

    @property
    def all_created(self):
        o = []
        for e in self.events:
            if e.type == 'Create': o.append(e)
        return o

    @property
    def all_created_instances(self):
        o = []
        model_names = 'periodical,movement,person,illustration,publisher'
        model_names += ',publication,text'
        for e in self.events:
            if e.type == 'Create' and e.model_name in model_names: 
                o.append(e)
        return o

    @property
    def created(self):
        for e in self.events:
            if e.type == 'Create':
                return  e.username + ' ' + e.time_str
        return 'user unknown'

    @property
    def created_time(self):
        for e in self.events:
            if e.type == 'Create':
                return e.time_str
        return ''

    @property
    def created_by(self):
        for e in self.events:
            if e.type == 'Create':
                return  e.username 
        return 'user unknown'

    def _make_change_fields_string(self, e):# changed_fields):
        m = ''
        if self.user:
            if e.type == 'Create': return ['created a '+e.model_name + ': ' + e.object_str]
            m  = e.model_name+': ' + e.object_str + ' | '
        elif not e.changed and not e.related_name: return ['no changes']
        o = []
        for change in e.changes:
            if change.field == 'last_login': o.append('login')
            elif change.field == 'date_joined':pass
            else:
                m = str(change.field) +': '
                m += str(change.old_state) +' -> '
                m += str(change.new_state)
                o.append(m) 
        return o

    @property
    def username(self):
        return self.events[0].username


    @property
    def updates(self):
        events = []
        if self.related_name or self.user: events = [e for e in self.events]
        else: events = [e for e in self.events if e.type =='Update']
        if self.add_related_events:
            for crud in self.cruds:
                events.extend( crud.events )
        return sorted(events,reverse = True)


    @property
    def anychanges(self):
        return True if self.updates else False
        
    @property
    def updates_str_hide_user(self):
        return self._updates_str(show_user=False)

    @property
    def updates_str(self):
        return self._updates_str()

    def _updates_str(self, show_user = True):
        o = []
        for e in self.updates:
            cfs = self._make_change_fields_string(e)
            for cf in cfs:
                line = [e.username,e.time_str,cf] if show_user else [e.time_str,cf]
                o.append([' | '.join(line),e.link])
        if o == []: return 'no updates'
        return o

    @property
    def last_update(self):
        events = self.updates
        if len(events) == 0: return 'unknown'
        e = events[0]
        if len(events) ==1 and e.type == 'Create':
            cf = 'created'
        else:
            cf = ' | '.join(self._make_change_fields_string(e))
        return ' // '.join([e.time_str,e.username,cf])

    @property
    def last_update_time(self):
        if len(self.events) == 0: return 'time unknown'
        return self.events[0].time_str
    
    @property
    def last_update_by(self):
        if len(self.events) == 0: return 'user unknown'
        return self.events[0].username

class Event:
    def __init__(self,e, related_name = '',related_instance = None):
        self.event = e
        self.related_name = related_name
        self.related_instance = related_instance
        self.type = e.get_event_type_display()
        self.changed = True if e.changed_fields not in ['null',None] else False
        self.username = e.user.username if e.user else ''
        self.set_time()
        self.app_name = e.content_type.app_label
        self.model_name = e.content_type.model
        self.model_pk = e.object_id
        if self.changed: self.set_changes()
        elif related_name and self.type == 'Create':
            self.set_related_change()
        else: self.changes = []

    def __repr__(self):
        return str(self.type) + ' ' + str(self.username) 

    def __lt__(self,other):
        return self.epoch < other.epoch

    def set_changes(self):
        try: self.cf_dict = eval(self.event.changed_fields)
        except: raise ValueError('could not create dict from:',
            self.event.changed_fields)
        self.changes = [Change(self.username,self.time_str,k,self.cf_dict[k],
            self.related_name,self.related_instance) for k in self.cf_dict.keys()]

    def set_related_change(self):
        self.changes = [Change(self.username,self.time_str,self.related_name +' (created)',
            ['',self.related_instance.__str__()],'')]

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

    @property
    def model(self):
        if not hasattr(self,'_model'):
            try:self._model = apps.get_model(self.app_name,self.model_name)
            except:self._model = False
        return self._model
            
    @property
    def object_str(self):
        try:return self.model.objects.get(pk = self.model_pk).__str__()
        except: return 'an object that has been deleted'

    @property
    def link(self):
        " creates an href link to the edit page of the changed object."
        if self.model_name in ['userloc','geoloc','user'] or self.app_name == 'auth': return ''
        if 'relation' in self.model_name:
            model = self.model
            try:instance = model.objects.get(pk = self.model_pk)
            except: return ''
            if not hasattr(instance,'primary'):return ''
            print(model,instance.primary)
            app_name, model_name = instance2names(instance.primary) 
            return "/"+app_name+"/edit_"+model_name.lower()+"/"+str(instance.primary.pk)
        return "/"+self.app_name +"/edit_"+self.model_name.lower()+"/"+str(self.model_pk)
        
                

class Change:
    def __init__(self,user,time,field_name,state,related_name,related_instance = None):
        self.username = user
        self.time = time
        self.field= related_name + ' | ' + field_name if related_name else field_name
        if len(state) == 0: self.old_state =''
        else:self.old_state = state[0]
        if len(state) < 2: self.new_state = 'no new state'
        elif not related_instance or not related_name: self.new_state = state[1]
        else: self.new_state = state[1] + ' (' + related_instance.__str__() +')'
            
        self.related_name = related_name

    def __repr__(self):
        return str(self.field) + ' ' + str(self.username) + ' ' + self.time

class Tab:
    def __init__(self,tab_names,focus=0):
        if type(tab_names) != list: self.tab_names = tab_names.split(',')
        else: self.tab_names = tab_names
        self.ntabs = len(self.tab_names)
        self.focus = self.tab_names[focus]
        if focus >= self.ntabs: self.focus = self.tab_names[0]

    def __repr__(self):
        return ' '.join(self.tab_names)

class Tabs:
    def __init__(self,tabs,names,focus_names = ''):
        self.tabs = tabs
        if type(names) != list: self.names = names.split(',')
        else: self.names = names
        for name, tab in zip(self.names,self.tabs):
            setattr(self,name,tab)
        if focus_names: 
            if type(focus_names) != list: self.focus = focus_names.split(',')
            else: self.focus = focus_names
        else: self.focus = [t.focus for t in self.tabs]


def make_tabs(tab_type,focus=0,focus_names = ''):
    minimize = Tab('Edit,Minimize',focus)
    print(tab_type)
    if focus_names == 'default': focus_names=''
    if tab_type == 'person':
        t = 'Locations,Texts,Illustrations,Publisher-Manager,Pseudonym,Movements,Persons'
        t += ',Periodicals'
        relations = Tab(t,focus)
        return Tabs([minimize,relations],'minimize,relations',focus_names)
    if tab_type == 'publication':
        t = 'Texts,Illustrations,Periodical,ReviewedByText'
        relations = Tab(t,focus)
        return Tabs([minimize,relations],'minimize,relations',focus_names)
    if tab_type == 'text':
        t = 'Texts,Persons,Publications,PublicationReview'
        relations = Tab(t,focus)
        return Tabs([minimize,relations],'minimize,relations',focus_names)
    if tab_type == 'illustration':
        t = 'Illustrations,Persons,Publications'
        relations = Tab(t,focus)
        return Tabs([minimize,relations],'minimize,relations',focus_names)
    if tab_type == 'movement':
        t = 'Persons'
        relations = Tab(t,focus)
        return Tabs([minimize,relations],'minimize,relations',focus_names)
    if tab_type == 'periodical':
        t = 'Publications,Persons'
        relations = Tab(t,focus)
        return Tabs([minimize,relations],'minimize,relations',focus_names)
    if tab_type == 'location':
        t = 'Contained by'
        relations = Tab(t,focus)
        return Tabs([minimize,relations],'minimize,relations',focus_names)
        

        
