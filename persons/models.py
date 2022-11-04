from django.db import models
from django.utils import timezone
from django import urls
import json
from locations.models import Location
from utilities.models import Language, RelationModel,GroupTag 
from utils.model_util import id_generator, info,instance2names, get_empty_fields
from utils.map_util import field2locations, pop_up, get_location_name,gps2latlng
from utilities.models import SimpleModel


def make_simple_model(name):
    '''create a simple model for a given name based on the 
    abstract model SimpleModel
    '''
    exec('class '+name + '(SimpleModel,info):\n\tpass',globals())

#for each name listed below, create a simple model
names = 'Pseudonym,PersonPersonRelationType,PersonLocationRelationType'
names += ',PersonTextRelationRole,PersonPeriodicalRelationRole'
names += ',PersonIllustrationRelationRole,MovementType'
names += ',PersonMovementRelationRole'
names = names.split(',')

for name in names:
    make_simple_model(name)

# --- main models ---

class Person(models.Model, info):
    '''A person with a specific role e.g. author, writer, etc.'''
    dargs = {'on_delete':models.SET_NULL,'default':None,'null':True}
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    full_name = models.CharField(max_length=900, null=True, blank=True)
    SEX= [('female','female'),('male','male'),('other','other'),
        ('unknown','unknown')]
    sex = models.CharField(max_length=15,choices=SEX)
    pseudonym= models.ManyToManyField(Pseudonym,blank=True)
    birth_year = models.PositiveIntegerField(null=True,blank=True)
    death_year = models.PositiveIntegerField(null=True,blank=True)
    birth_place= models.ForeignKey(Location, related_name = 'hborn', **dargs)
    death_place= models.ForeignKey(Location, related_name = 'hdied', **dargs)
    notes = models.TextField(blank=True,null=True) 
    description = models.TextField(blank=True)
    complete = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    incomplete= models.BooleanField(default=False)
    location_field = 'birth_place'
    gps = models.CharField(max_length=300,default ='')
    gps_names = models.CharField(max_length=4000,default='')
    loc_ids = models.CharField(max_length=300,default ='')
    group_tags= models.ManyToManyField(GroupTag,blank=True, default= None)
    source_link= models.CharField(max_length=1000,blank=True,null=True)
    connection_count = models.PositiveIntegerField(null=True,blank=True) 

    def save(self,*args,**kwargs):
        '''set gps location information on the person instance to 
        speed up map rendering.
        '''
        super(Person,self).save(*args,**kwargs)
        old_gps = self.gps
        self._set_gps()
        self._set_full_name()
        if self.gps != old_gps:super(Person,self).save()
        super(Person,self).save(*args,**kwargs)

    def _set_connection_count(self):
        from utils import instance_links
        links = instance_links.Links(self)
        self.connection_count = links.n_connections
        self.save()

    def empty_fields(self,fields = []):
        return get_empty_fields(self,fields, default_is_empty = True)

    def _set_gps(self):
        '''sets the gps coordinates and name of related location to 
        speed up map visualization.
        '''
        locations = field2locations(self,self.location_field)
        if locations:
            gps = ' | '.join([l.gps for l in locations if l.gps])
            names= ' | '.join([l.name for l in locations if l.gps])
            ids = ','.join([str(l.pk) for l in locations])
            self.gps = gps
            self.gps_names = names
            self.loc_ids = ids
        else: self.gps, self.gps_names,self.loc_ids = '','',''

    def _set_full_name(self):
        full_name = self.name 
        pseudonyms = self.pseudonyms
        if pseudonyms: full_name += ' (' + pseudonyms + ')'
        self.full_name = full_name
            
    class Meta:
        unique_together = 'first_name,last_name,birth_year'.split(',')

    @property
    def get_dates(self):
        if not self.birth_year:return ''
        return [self.birth_year]

    @property
    def identifier(self):
        i = self._meta.app_label + '_' + self._meta.model_name 
        i += '_' + str( self.pk )
        return i

    @property
    def name(self):
        if self.first_name == None: return self.last_name
        if self.last_name == None: return self.first_name
        return str(self.first_name) + ' ' + str(self.last_name)

    @property
    def instance_name(self):
        return self.name
    
    def __str__(self):
        return self.name

    @property
    def born(self):
        return self.birth_year

    @property
    def died(self):
        return self.death_year

    @property
    def life(self):
        m =''
        if self.born:m += 'born ' + str(self.birth_year) 
        if self.born and self.died: m += ', '
        if self.died:m += 'died ' + str(self.death_year)
        if self.born and self.died: 
            m += ' (age ' + str(self.death_year -self.birth_year) + ')'
        return m

    @property
    def life_concise(self):
        m =''
        if self.born and not self.died: m += 'born '
        if self.born:m += str(self.birth_year) 
        if self.born and self.died: m += ' - '
        if self.died and not self.born: m += 'died '
        if self.died:m += str(self.death_year)
        return m

    @property
    def gender(self):
        try:return dict(self.SEX)[self.sex]
        except:return ''

    @property
    def latlng(self):
        '''float tuple representation of the gps coordinates.
        '''
        return gps2latlng(self.gps)

    @property
    def latlng_names(self):
        '''return a list of location names.
        '''
        try: return self.gps_names.split(' - ')
        except: return None

    @property
    def location_string(self):
        try:return ', '.join(self.latlng_names)
        except: return ''

    @property
    def pseudonyms(self):
        '''string representation of listed pseudonyms.
        '''
        return ' | '.join([x.name for x in self.pseudonym.all()])

    @property
    def type_to_locations_dict(self):
        if hasattr(self,'_type_location_dict'): return self._type_location_dict
        d ={}
        plrs = self.personlocationrelation_set.all()
        for plr in plrs:
            if plr.relation.name.lower() not in d.keys(): 
                d[plr.relation.name.lower()] = []
            d[plr.relation.name.lower()].append(plr.location.full_name)
        self._type_location_dict= d
        return self._type_location_dict

    @property
    def texts(self):
        if hasattr(self,'_texts'): return self._texts
        output = []
        for texts in self.role_to_text_dict.values():
            output.extend(texts)
        self._texts= sorted(output, key = lambda x: x.title)
        return self._texts

    @property
    def text_settings(self):
        if hasattr(self,'_text_settings'): return self._text_settings
        settings = []
        for text in self.texts:
            if text.setting and text.setting not in settings: 
                settings.append(text.setting)
        self._text_settings = sorted(settings)
        return self._text_settings

    @property
    def illustrations(self):
        if hasattr(self,'_illustrations'): return self._illustrations
        output = []
        for illustrations in self.role_to_illustration_dict.values():
            output.extend(illustrations)
        self._illustrations= sorted(output, key = lambda x: x.caption)
        return self._illustrations

    @property
    def publications(self):
        if hasattr(self,'_publications'): return self._publications
        items = self.texts + self.illustrations
        output = []
        for item in items:
            for publication in item.publications:
                if not publication in output: output.append(publication)
        self._publications = sorted(output, key = lambda x: x.date)
        return self._publications

    @property
    def publication_locations(self):
        if hasattr(self,'_publication_locations'): return self._publication_locations
        locations = []
        for publication in self.publications:
            for location in publication.location.all():
                if location and location.name not in locations:
                    locations.append(location.name)
        self._publication_locations = sorted(locations)
        return self._publication_locations
        
    @property
    def role_to_person_dict(self):
        if hasattr(self,'_role_to_person_dict'): return self._role_to_person_dict
        d ={}
        for relation_type in PersonPersonRelationType.objects.all():
            persons = self.get_linked_persons(relation_type.name)
            if not persons: continue
            d[relation_type.name.lower()] = sorted(persons, key = lambda x:x.last_name)
        self._role_to_person_dict = d
        return self._role_to_person_dict

    def get_linked_persons(self,relation_type):
        persons = []
        person_links = self.person1.filter(relation_type__name__icontains=relation_type) 
        for person_link in person_links:
            person = person_link.person2
            if person not in persons:persons.append(person)
        person_links = self.person2.filter(relation_type__name__icontains=relation_type) 
        for person_link in person_links:
            person = person_link.person1
            if person not in persons:persons.append(person)
        return persons


    @property
    def role_to_text_dict(self):
        if hasattr(self,'_role_to_text_dict'): return self._role_to_text_dict
        d ={}
        for ptr in self.persontextrelation_set.all():
            if ptr.relation_name.lower() not in d.keys(): 
                d[ptr.relation_name.lower()] = []
            d[ptr.relation_name.lower()].append(ptr.text)
        for role,texts in d.items():
            d[role] = sorted(texts, key = lambda x:x.title)
        self._role_to_text_dict= d
        return self._role_to_text_dict

    @property
    def role_to_movement_dict(self):
        if hasattr(self,'_role_to_movement_dict'): return self._role_to_movement_dict
        d ={}
        for pmr in self.personmovementrelation_set.all():
            if pmr.role.name.lower() not in d.keys(): 
                d[pmr.role.name.lower()] = []
            d[pmr.role.name.lower()].append(pmr.movement)
        for role,movements in d.items():
            d[role] = sorted(movements, key = lambda x:x.name)
        self._role_to_movement_dict= d
        return self._role_to_movement_dict

    @property
    def role_to_periodical_dict(self):
        if hasattr(self,'_role_to_periodical_dict'): return self._role_to_periodical_dict
        d ={}
        for ppr in self.personperiodicalrelation_set.all():
            if ppr.role.name.lower() not in d.keys(): 
                d[ppr.role.name.lower()] = []
            d[ppr.role.name.lower()].append(ppr.periodical)
        for role,periodicals in d.items():
            d[role] = sorted(periodicals, key = lambda x:x.title)
        self._role_to_periodical_dict= d
        return self._role_to_periodical_dict

    @property
    def role_to_illustration_dict(self):
        if hasattr(self,'_role_to_illustration_dict'): 
            return self._role_to_illustration_dict
        d ={}
        for pir in self.personillustrationrelation_set.all():
            if pir.role.name.lower() not in d.keys(): 
                d[pir.role.name.lower()] = []
            d[pir.role.name.lower()].append(pir.illustration)
        for role,texts in d.items():
            d[role] = sorted(texts, key = lambda x:x.caption)
        self._role_to_illustration_dict= d
        return self.role_to_illustration_dict

    @property
    def roles(self):
        if hasattr(self,'_roles'): return self._roles
        roles = []
        s = self
        relation_sets = [s.personillustrationrelation_set,s.persontextrelation_set]
        relation_sets.append(s.personmovementrelation_set)
        relation_sets.append(s.personperiodicalrelation_set)
        for relation_set in relation_sets:
            for x in relation_set.all():
                if x.role.name not in roles:roles.append(x.role.name)
        self._roles = roles
        return self._roles

    @property
    def vocations(self):
        output = []
        vocation_list = 'author,illustrator'.split(',')
        for vocation in vocation_list:
            if vocation in self.roles: output.append(vocation)
        publisher_relations = self.manager.all() 
        if publisher_relations: output.append('publisher')
        return ', '.join(output)

    @property
    def publishers(self):
        if hasattr(self,'_publishers'): return self._publishers
        publisher_relations = self.manager.all() 
        output = []
        for pr in publisher_relations:
            output.append(pr.publisher)
        self._publishers = output
        return self._publishers
        
    def pop_up(self,latlng=None):
        '''create a pop up for map rendering with information 
        about this instance.
        '''
        m = ''
        if self.life: m += '<p><small>' + self.life + '</small></p>'
        pseudonyms = self.pseudonyms
        if pseudonyms: 
            m += '<p><small>pseudonym <b>' + pseudonyms + '</b></small></p>'
        p = pop_up(self, latlng, extra_information = m)
        return p

    def plot(self):
        '''create an information dictionary that can be used to retrieve 
        this instance from the database.
        '''
        app_name, model_name = instance2names(self) 
        gps = str(self.gps.split(' | ')).replace("'",'')
        d = {'app_name':app_name, 'model_name':model_name, 
            'gps':gps, 'pk':self.pk}
        if d['gps'] == '[]': self._set_secondary_place(d)
        return d

    def _set_secondary_place(self,d):
        '''if the default location used for plotting a person is not present
        use an alternatively specified location to plot it on the map
        '''
        ptd = self.make_placetype_dict()
        for relation_name in ptd:
            if 'residence' == relation_name: 
                d['gps'] = '[' + ptd[relation_name][0] + ']'
                break
            d['gps'] = '[' + ptd[relation_name][0] + ']'
        

    def latlng2placetype(self,latlng):
        '''return the relation between the place and the person,
         e.g. residence.
        '''
        try:
            ptd = self.make_placetype_dict()
            for relation_name in ptd:
                if 'location_name' in relation_name: continue
                for gps in ptd[relation_name]:
                    if eval(gps) == latlng: return relation_name.replace('_',' ')
            self.view()
        except:pass
        return ''

    def latlng2name(self,latlng):
        '''returns the location name based on on the latlng input
        uses index of gps corresponding with latlng and 
        gps_names to return correct name
        '''
        ln = get_location_name(self,latlng)
        if ln == '':
            try:
                ptd = self.make_placetype_dict()
                for relation_name in ptd:
                    if 'location_name' in relation_name: continue
                    for i,gps in enumerate(ptd[relation_name]):
                        if eval(gps) ==latlng: ln = ptd[relation_name+'_location_name'][i]
            except:pass
        pt = self.latlng2placetype(latlng)
        if ln and pt: return '<b>'+ln + '</b>, ' + pt
        if ln: return ln
        return pt
        
    def make_placetype_dict(self):
        '''creates a dictionary that maps the relation name between the 
        person and location
        to the gps string saved on the person instance
        [relation name] + '_location_name' gives the corresponding location name
        '''
        d = {}
        for name in  'birth_place,death_place'.split(','):
            if hasattr(self,name):
                try: 
                    d[name] = [getattr(self,name).gps]
                    d[name+'_location_name'] = [getattr(self,name).name]
                except:continue
        for plr in self.personlocationrelation_set.all():
            names = 'location,person,relation'.split(',')
            if None in [getattr(plr,n) for n in names]:continue
            if plr.relation.name not in d.keys():
                d[plr.relation.name] = []
                d[plr.relation.name +'_location_name'] = []
            d[plr.relation.name].append( plr.location.gps )
            d[plr.relation.name+'_location_name'].append( plr.location.name )
        return d

    @property
    def sidebar_info(self):
        d = {}
        d['name'] = self.instance_name
        d['date'] = self.life
        d['detail_url'] = urls.reverse_lazy(self.detail_url, args = [self.pk])
        d['extra'] = self.gender
        d['identifier'] = self.identifier
        d['connection_count'] = self.connection_count
        return d

    @property
    def edit_url(self):
        return self._meta.app_label + ':edit_' + self._meta.model_name

    @property
    def detail_url(self):
        return self._meta.app_label + ':detail_' + self._meta.model_name

    
class Movement(models.Model, info):
    '''A movement (e.g. literary) a collection of persons.'''
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    name = models.CharField(max_length=200, null=True, blank=True)
    movement_type = models.ForeignKey(MovementType,**dargs)
    location= models.ForeignKey(Location,**dargs)
    founded = models.PositiveIntegerField(null=True,blank=True) 
    closure = models.PositiveIntegerField(null=True,blank=True) 
    notes = models.TextField(null=True,blank=True) # many to many
    description = models.TextField(blank=True)
    complete = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    incomplete = models.BooleanField(default=False)
    gps = models.CharField(max_length=300,default ='')
    gps_names = models.CharField(max_length=4000,default='')
    loc_ids = models.CharField(max_length=300,default ='')
    location_field = 'location'
    person = models.CharField(max_length=2000,blank=True,null=True)
    connection_count = models.PositiveIntegerField(null=True,blank=True) 

    def _set_connection_count(self):
        from utils import instance_links
        links = instance_links.Links(self)
        self.connection_count = links.n_connections
        self.save()

    def _set_person(self):
        names = [] 
        for pmr in self.personmovementrelation_set.all():
            names.append(pmr.person.full_name)
        self.person = '; '.join(names)
        self.save()

    def save(self,*args,**kwargs):
        super(Movement,self).save(*args,**kwargs)
        old_gps = self.gps
        self._set_gps()
        if self.gps != old_gps:super(Movement,self).save()
        super(Movement,self).save(*args,**kwargs)

    @property
    def get_dates(self):
        if not self.founded:return ''
        return [self.founded]

    @property
    def dates(self):
        o =''
        if self.founded: o += 'founded in: ' +str(self.founded) + ' '
        if self.closure: o += 'closure in: ' +str(self.closure)
        return o
        

    @property
    def identifier(self):
        i = self._meta.app_label + '_' + self._meta.model_name 
        i += '_' + str( self.pk )
        return i

    @property
    def edit_url(self):
        return self._meta.app_label + ':edit_' + self._meta.model_name

    @property
    def detail_url(self):
        return self._meta.app_label + ':detail_' + self._meta.model_name

    def empty_fields(self,fields = []):
        return get_empty_fields(self,fields, default_is_empty = True)

    @property
    def role_to_person_dict(self):
        if hasattr(self,'_role_to_person_dict'): return self._role_to_person_dict
        d ={}
        for pmr in self.personmovementrelation_set.all():
            role = pmr.role.name.lower()
            if not role in d.keys(): d[role] = []
            d[role].append(pmr.person)
        for role,persons in d.items():
            d[role] = sorted(persons, key = lambda x:x.last_name)
        self._role_to_person_dict = d
        return self._role_to_person_dict
        

    def _set_gps(self):
        '''sets the gps coordinates and name of related location to speed 
        up map visualization.
        '''
        locations = field2locations(self,self.location_field)
        if locations:
            gps = ' | '.join([l.gps for l in locations if l.gps])
            names= ' | '.join([l.name for l in locations if l.gps])
            ids = ','.join([str(l.pk) for l in locations])
            self.gps = gps
            self.gps_names = names
            self.loc_ids = ids
        else: self.gps, self.gps_names,self.loc_ids = '','',''

    class Meta:
        unique_together = 'name,founded'.split(',')

    def __str__(self):
        return self.name

    @property
    def location_str(self):
        return self.location_string

    @property
    def latlng(self):
        return gps2latlng(self.gps)

    @property
    def latlng_names(self):
        try: return self.gps_names.split(' || ')
        except: return None

    @property
    def location_string(self):
        try:return ', '.join(self.latlng_names)
        except: return ''

    def pop_up(self,latlng):
        m = ''
        if self.movement_type: 
            m += '<p><small><b>' + self.movement_type.name 
            m += '</b> movement</small></p>'
        if self.founded: m += '<p><small>founded <b>' + str(self.founded)
        if self.founded and self.closure: m += '</b>, '
        else: m += '</b></small></p>'
        if not m and self.founded: m += '<p><small>'
        if self.closure: 
            m += 'closure <b>' + str(self.closure) + '</b></small></p>'
        return pop_up(self,latlng,extra_information=m)


    @property
    def instance_name(self):
        return self.name

    def plot(self):
        app_name, model_name = instance2names(self) 
        gps = str(self.gps.split(' | ')).replace("'",'')
        d = {'app_name':app_name, 'model_name':model_name, 
            'gps':gps, 'pk':self.pk}
        return d

    def latlng2name(self,latlng):
        return get_location_name(self,latlng)

    @property
    def type_info(self):
        if self.movement_type: return self.movement_type.name
        return '' 

    @property
    def sidebar_info(self):
        d = {}
        d['name'] = self.instance_name
        d['date'] = self.dates
        d['detail_url'] = urls.reverse_lazy(self.detail_url, args = [self.pk])
        d['extra'] = self.type_info
        d['identifier'] = self.identifier
        d['connection_count'] = self.connection_count
        return d


# --- relational models ---

class PersonPersonRelation(RelationModel, info):
    '''Relation between persons. Assumed to be symmetrical.'''
    person1 = models.ForeignKey(Person, on_delete=models.CASCADE,
        related_name='person1')
    person2 = models.ForeignKey(Person, on_delete=models.CASCADE,
        related_name='person2')
    relation_type = models.ForeignKey(PersonPersonRelationType, 
        on_delete=models.CASCADE)
    model_fields = ['person1','person2']
    relation_field = 'relation_type'

    class Meta:
        constraints = [models.UniqueConstraint(
            fields='person1,person2,relation_type'.split(','), 
            name = 'unique_personpersonrelation')]


    @property
    def relation_name(self):
        return self.relation.name

class PersonLocationRelation(RelationModel,info):
    '''relation between person and location.'''
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE,
        default=None,null=True)
    relation = models.ForeignKey(PersonLocationRelationType, null=True, 
        on_delete=models.SET_NULL)
    start_year = models.PositiveIntegerField(null=True,blank=True)
    end_year = models.PositiveIntegerField(null=True,blank=True)
    location_name = models.CharField(max_length=200, default='',null=True)
    person_name = models.CharField(max_length=200, default='',null=True)
    description= models.TextField(null=True,blank=True)
    location_field = 'location'
    model_fields = ['person','location']
    relation_field = 'relation'

    @property
    def relation_name(self):
        return self.relation.name

    def __str__(self):
        try:
            r = self.relation.name
            return ', '.join([self.person.name, self.location.name, r])
        except:
            self.view()
            return 'could not generate str representation'

    @classmethod
    def create(cls):
        if hasattr(cls,'location'):
            cls.location_name = cls.location.name
        if hasattr(cls,'person'):
            cls.person_name = cls.person.first_name + ' ' + cls.person.last_name

    @property
    def primary(self):
        return self.person


    def pop_up(self,main_instance=None, latlng =None):
        m = self.person.pop_up(self.location.latlng)    
        return m

    @property
    def instance_name(self):
        return self.__str__()

    def plot(self):
        d = super().plot()
        d['layer_name'] = 'Person'
        return d

    '''
    def plot(self):
        app_name, model_name = instance2names(self) 
        pan, pmn= instance2names(self.person) 
        gps = str(self.location.gps.split(' | ')).replace("'",'')
        d = {'app_name':app_name, 'model_name':model_name, 
            'gps':gps, 'pk':self.pk,'layer_name':pmn}
        return d
    '''


class PublisherManager(models.Model): #or broker
    '''Person that manages writers.'''
    # Publisher= apps.get_model('catalogue','Publisher')
    publisher = models.ForeignKey('catalogue.Publisher', 
        on_delete=models.CASCADE, related_name='publisher')
    manager = models.ForeignKey(Person, on_delete=models.CASCADE,
        related_name='manager')
    model_fields = ['person','location']

    @property
    def relation_name(self):
        return 'Manager'

class PersonTextRelation(RelationModel, info):
    '''Relation between a person and a text.'''
    role = models.ForeignKey(PersonTextRelationRole, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    text = models.ForeignKey('catalogue.Text', null=True, blank=True, 
        on_delete=models.CASCADE)
    published_under = models.CharField(max_length = 100,null=True,blank=True)
    model_fields = ['person','text']
    relation_field = 'role'
    
    def __str__(self):
        m = self.person.__str__() + ' | ' + self.role.__str__() 
        m += ' | ' + self.text.__str__()
        return m

    @property
    def relation_name(self):
        return self.role.name

    class Meta:
        unique_together = ['role','person','text']

    @property
    def primary(self):
        return self.person

    def pop_up(self,main_instance):
        m = super().pop_up(main_instance)
        m += '<small>'+self.person.name + ' is the <b>' 
        m += self.relation_name + '</b></small>'
        return m

    '''
    def pop_up(self,main_instance,latlng = None):
        self.set_other(main_instance)
        if not self.other: return 'could not construct relation'
        latlng = gps2latlng(self.other.gps)
        m = self.other.pop_up(latlng)
        m += '<small>'+self.person.name + ' is the <b>' +self.relation_name 
        m += '</b></small>'
        return m

    def set_other(self,main_instance):
        if main_instance == self.person: self.other = self.text
        elif main_instance == self.text: self.other = self.person
        else: self.other = False
        
    def plot(self):
        app_name, model_name = instance2names(self) 
        oan,omn = instance2names(self.other)
        gps = str(self.other.gps.split(' | ')).replace("'",'')
        d = {'app_name':app_name, 'model_name':model_name, 
            'gps':gps, 'pk':self.pk,'layer_name':omn}
        return d
    '''



class PersonIllustrationRelation(RelationModel, info):
    '''Relation between a person and an illustration.'''
    role = models.ForeignKey(PersonIllustrationRelationRole, 
        on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    illustration= models.ForeignKey('catalogue.Illustration', null=True, 
        blank=True, on_delete=models.CASCADE)
    model_fields=['person','illustration']
    
    def __str__(self):
        m = self.person.__str__() + ' | ' + self.role.__str__() 
        m += ' | ' + self.illustration.__str__()
        return m

    class Meta:
        unique_together = ['role','person','illustration']

    @property
    def primary(self):
        return self.person


class PersonMovementRelation(RelationModel, info):
    '''Relation between a movement and a person.'''
    movement = models.ForeignKey(Movement, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.ForeignKey(PersonMovementRelationRole, 
        on_delete=models.CASCADE)
    model_fields = ['movement','person']
    relation_field = 'role'

    def __str__(self):
        m = self.person.__str__() + ' | ' + self.role.__str__() 
        m +=' | of movement: '
        m += self.movement.__str__() 
        return m

    @property
    def relation_name(self):
        return self.role.name

    @property
    def primary(self):
        return self.person

    def pop_up(self,main_instance):
        m = super().pop_up(main_instance)
        m += '<small>Role: <b>'+self.relation_name + '</b></small>'
        return m

    '''
    def pop_up(self,main_instance,latlng = None):
        self.set_other(main_instance)
        if not self.other: return 'could not construct relation'
        latlng = gps2latlng(self.other.gps)
        m = self.other.pop_up(latlng)
        m += '<small>Role: <b>'+self.relation_name + '</b></small>'
        return m

    def set_other(self,main_instance):
        if main_instance == self.person: self.other = self.movement
        elif main_instance == self.movement: self.other = self.person
        else: self.other = False

    def plot(self):
        app_name, model_name = instance2names(self) 
        oan,omn = instance2names(self.other)
        gps = str(self.other.gps.split(' | ')).replace("'",'')
        d = {'app_name':app_name, 'model_name':model_name, 
            'gps':gps, 'pk':self.pk,'layer_name':omn}
        return d
    '''

class PersonPeriodicalRelation(RelationModel, info):
    '''Relation between a periodical and a person.'''
    periodical = models.ForeignKey('catalogue.Periodical', 
        on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.ForeignKey(PersonPeriodicalRelationRole, 
        on_delete=models.CASCADE)
    model_fields = ['periodical','person']
    relation_field = 'role'

    def __str__(self):
        m = self.person.__str__() + ' | ' + self.role.__str__() 
        m +=' | of periodical: '
        m += self.periodical.__str__() 
        return m

    @property
    def relation_name(self):
        return self.role.name

    @property
    def primary(self):
        return self.person

    def pop_up(self,main_instance):
        m = super().pop_up(main_instance)
        m += '<small>Role: '+self.role.name + '</small>'
        return m

    '''
    def pop_up(self,main_instance,latlng = None):
        self.set_other(main_instance)
        if not self.other: return 'could not construct relation'
        latln = gps2latlng(self.other.gps)
        m = self.other.pop_up(latlng)
        m += '<small>Role: '+self.role.name + '</small>'
        return m

    def set_other(self,main_instance):
        if main_instance == self.person: self.other = self.periodical
        elif main_instance == self.periodical: self.other = self.person
        else: self.other = False
    
    def plot(self):
        app_name, model_name = instance2names(self) 
        oan,omn = instance2names(self.other)
        gps = str(self.other.gps.split(' | ')).replace("'",'')
        d = {'app_name':app_name, 'model_name':model_name, 
            'gps':gps, 'pk':self.pk,'layer_name':omn}
        return d
    '''
