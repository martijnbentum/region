from django.apps import apps
from django.db.models.functions import Lower
from django.db.models import Q
import time
from utils.model_util import get_all_models, instance2names
from utils.model_util import instances2model_counts, instances2genre_counts
from utils.model_util import instances2texttype_counts, instances2language_counts
from utils.model_util import instances2gender_counts, instances2locationtype_counts


class SearchAll:
    def __init__(self,request = None, models = [], query = None, 
        max_entries=False, special_terms = None ):
        '''searches all (specified/relevant) models. 
        request         contains query, direction, sorting_option which
                        can be overwritten by the parameters
        models          list of models to search by default it contains
                        all relevant models defined in model_util
        query           parameter to directly pass a query overwrites
                        query passed in the request. A query is a string
                        with optional special terms starting with $ or *
        special_terms   parameter to pass optional special terms such as combine
        '''
                            
        if not models: models = get_all_models()
        self.models = models
        self.query =query
        self.special_terms = special_terms
        self.searches = []
        for model in self.models:
            an, mn = instance2names(model)
            s = Search(request,mn,an,query,max_entries,
                special_terms = special_terms)
            self.searches.append(s)
        self.query = self.searches[0].query.query

    def __repr__(self):
        m = 'Search all object\n'
        m += '\n'.join([x.__repr__() for x in self.searches])
        return m

    def filter(self, verbose= False, separate = False):
        if hasattr(self,'_instances'): return self._instances
        self._instances = []
        for s in self.searches:
            self._instances.extend(s.filter())
        if verbose:self.searches[0].n
        return self._instances


    def country_filter(self, countries = []):
        if not hasattr(self,'instances'):self.filter()
        if not hasattr(self,'_country_counts'):
            i = self._instances
            cc, ci= instances2country_counts(i)
            self._country_counts, self._country_instances=cc, ci
            country_identifiers=_instance2identifier_dict(self._country_instances)
            self._country_identifiers=country_identifiers
        if countries:
            instances = filter_on_list(self._country_instances, countries)
            return instances

    def model_filter(self, model_names = []):
        if not hasattr(self,'instances'): self.filter()
        if not hasattr(self,'_model_counts'):
            c,i = instances2model_counts(self._instances)
            self._model_counts, self._model_instances = c,i
            self._model_identifiers=_instance2identifier_dict(i)
        if model_names:
            instances = filter_on_list(self._model_instances, model_names)
            return instances

    def texttype_filter(self, texttype_names = []):
        if not hasattr(self,'instances'): self.filter()
        if not hasattr(self,'_texttype_counts'):
            counts, instances = instances2texttype_counts(self._instances)
            self._texttype_counts = counts
            self._texttype_instances = instances
            self._texttype_identifiers = _instance2identifier_dict(instances)
        if texttype_names:
            instances = filter_on_list(instances, texttype_names)
            return instances

    def language_filter(self, language_names = []):
        if not hasattr(self,'instances'): self.filter()
        if not hasattr(self,'_language_counts'):
            counts, instances = instances2language_counts(self._instances)
            self._language_counts = counts
            self._language_instances = instances
            self._language_identifiers = _instance2identifier_dict(instances)
        if language_names:
            instances = filter_on_list(instances, language_names)
            return instances

    def genre_filter(self, genre_names = []):
        if not hasattr(self,'instances'): self.filter()
        if not hasattr(self,'_genre_counts'):
            counts, instances = instances2genre_counts(self._instances)
            self._genre_counts = counts
            self._genre_instances = instances
            self._genre_identifiers = _instance2identifier_dict(instances)
        if genre_names:
            instances = filter_on_list(instances, language_names)
            return instances

    def gender_filter(self, gender_names = []):
        if not hasattr(self,'instances'): self.filter()
        if not hasattr(self,'_gender_counts'):
            counts, instances = instances2gender_counts(self._instances)
            self._gender_counts = counts
            self._gender_instances = instances
            self._gender_identifiers = _instance2identifier_dict(instances)
        if gender_names:
            instances = filter_on_list(instances, gender_names)
            return instances

    def locationtype_filter(self, locationtype_names = []):
        if not hasattr(self,'instances'): self.filter()
        if not hasattr(self,'_locationtype_counts'):
            counts, instances = instances2locationtype_counts(self._instances)
            self._locationtype_counts = counts
            self._locationtype_instances = instances
            self._locationtype_identifiers = _instance2identifier_dict(instances)
        if locationtype_names:
            instances = filter_on_list(instances, locationtype_names)
            return instances
        

    def century_filter(self, centuries = []):
        if not hasattr(self,'instances'): self.filter()
        if not hasattr(self,'_century_counts'):
            c,i = instances2century_counts(self._instances)
            self._century_counts, self._century_instances = c,i
            self._century_identifiers=_instance2identifier_dict(i)
        century_names = _handle_centuries_input(centuries)
        if century_names:
            instances = filter_on_list(self._century_instances, century_names)
            return instances

    @property
    def country_counts(self):
        if not hasattr(self,'_country_counts'):self.country_filter()
        return self._country_counts

    @property
    def model_counts(self):
        if not hasattr(self,'_model_counts'):self.model_filter()
        return self._model_counts

    @property
    def texttype_counts(self):
        if not hasattr(self,'_texttype_counts'):self.texttype_filter()
        return self._texttype_counts

    @property
    def language_counts(self):
        if not hasattr(self,'_language_counts'):self.language_filter()
        return self._language_counts

    @property
    def genre_counts(self):
        if not hasattr(self,'_genre_counts'):self.genre_filter()
        return self._genre_counts

    @property
    def gender_counts(self):
        if not hasattr(self,'_gender_counts'):self.gender_filter()
        return self._gender_counts

    @property
    def locationtype_counts(self):
        if not hasattr(self,'_locationtype_counts'):self.locationtype_filter()
        return self._locationtype_counts

    @property
    def century_counts(self):
        if not hasattr(self,'_century_counts'):self.century_filter()
        return self._century_counts



class Search:
    '''search a django model on all fields or a subset with Q objects'''
    def __init__(self,request=None, model_name='',app_name='',query=None, 
        max_entries=500,active_fields = None,special_terms = None):
        '''search object to filter django models
        query               search terms provided by user
        search_fields       field set to restrict search (obsolete?)
        model_name          name of the django model
        app_name            name of the app of the model
        max_entries         restrict the number of entries in the search 
                            result to speed up 
                            rendering
        active_fields       extension the set the active field 
                            (can alternetively be done with flags in the query)
                            used in conjunction with buttons that set fields as 
                            active or not active
        special_terms       extension of setting search mode 
                            i.e. combining words or not / 
                            combining search fields or not
                            (can alternatively be done with flags in the query
                            used in conjunction with buttons that set the 
                            special terms 
                            active or not
        '''
        if query:
            self.query = Query(query=query,active_fields = active_fields,
                special_terms=special_terms)
            self.order = Order(order=get_foreign_keydict()[model_name.lower()])
        else:
            self.request = request
            self.query = Query(request,model_name, 
                active_fields = active_fields,special_terms=special_terms)
            self.order = self.query.order
        self.option = self.query.option
        self.max_entries = max_entries
        self.model_name = model_name
        self.app_name = app_name
        self.model = apps.get_model(app_name,model_name)
        self.fields = get_fields(model_name,app_name)
        self.select_fields()
        self.active_fields = [f.name for f in self.fields if f.include]
        self.search_fields = [f.name for f in self.fields if not f.exclude]
        self.notes = 'Search Fields: (' + ','.join(self.active_fields) + ')'

    def select_fields(self):
        '''select fields if one or more fields are specified, 
        otherwise all fields
        are searched (except those fields that are exclude by default e.g. id
        '''
        if self.query.fields and self.query.fields != ['']:
            for field in self.fields:
                if field.name in self.query.fields: field.include = True
                else: field.include = False

    def check_and_or(self, and_or):
        '''set whether the query should match in for all fields or 
        for one of the fields
        '''
        if and_or == '': 
            st = self.query.special_terms
            if 'and' in st or 'combine columns' in st: self.and_or = 'and'
            else: self.and_or = 'or'
        if self.and_or == 'and': self.notes += '\nall fields should match query'
        else: self.notes += '\none ore more fields should match query'

    def check_combine(self, combine):
        '''set whether word should be matched separately or as one string.
        '''
        self.combine = self.query.combine if combine == None else combine
        if self.combine:
            self.notes += '\ncombined query term: ' + self.query.clean_query
        else: 
            self.notes += '\nseperate query terms: ' 
            self.notes +=  ', '.join(self.query.query_terms)

    def check_completeness_approval(self):
        '''check whether complete and or approval should be checked.
        '''
        # print(self.result,9876)
        if self.query.completeness != None: 
            self.result = self.result.filter(complete=self.query.completeness)
            self.notes += '\ncompleteness: ' + str(self.query.completeness)
        if self.query.approval != None: 
            self.result = self.result.filter(approved=self.query.approval)
            self.notes += '\napproval: ' + str(self.query.approval)
        if self.query.incompleteness !=None: # whether an issue was flagged 
            self.result = self.result.filter(incomplete=self.query.incompleteness)
            self.notes += '\nincompleteness (issue): ' 
            self.notes += str(self.query.incompleteness)
        # print(self.result,54321)

    def exclude_doubles(self):
        '''exclude any instances that occur more than one time in the search output.
        '''
        o,pk = [],[]
        for instance in self.result:
            if instance.pk not in pk:
                pk.append(instance.pk)
                o.append(instance)
            else:continue
        self.result = o
            
    def set_ordering_and_direction(self):
        '''set on which field the search results should be orded and whether the
        ordering should be descending or ascending.
        '''
        if not self.order.order_results: return
        if self.order.order_by == 'connection_count':
            self.result = self.result.order_by(self.order.order_by)
        else:
            self.result = self.result.order_by(Lower(self.order.order_by))
        self.notes += '\nordered on field: ' + self.order.order_by
        if self.order.direction == 'descending': 
            self.result= self.result.reverse()
        self.notes += '\nordered in ' + self.order.direction + ' order'

    def select_empty(self):
        '''selects those instance that do not have a value in the specified 
        fields'''
        o = []
        start = time.time()
        # print(self.active_fields,3333)
        for instance in self.result:
            empty_fields = instance.empty_fields(self.active_fields)
            if self.and_or == 'and':
                ok = True
                for field in self.active_fields:
                    if field not in empty_fields:ok = False
            else:
                ok = False
                for field in self.active_fields:
                    if field in empty_fields:ok =True 
            if ok: o.append(instance)
        print('selecting empty instances duration:',delta(start))
        self.result = o
                    
            

    def filter(self, option = None,and_or='',combine= None):
        '''method to create q objects and filter instance from the database
        option      search term for filtering, default capital insensitive search
        and_or      whether q objects have an and/or relation
        seperate    whether the words in the query should be searched 
                    seperately or not
        '''
        start = time.time()
        if option == None: option = self.option
        self.check_and_or(and_or)
        print('and or check:',delta(start),'seconds')
        self.check_combine(combine)
        print('combine check:',delta(start),'seconds')
        self.qs = []
        for field in self.fields:
            if field.include: 
                if self.combine:
                    term = self.query.clean_query
                    self.qs.append(field.create_q(term=term,option=option))
                else:   
                    for term in self.query.query_terms:
                        self.qs.append(field.create_q(term=term,option=option))
        print('preparing q:',delta(start),'seconds')
        self.q = Q()
        for qobject in self.qs:
            if self.and_or == 'and': self.q &= qobject
            else: self.q |= qobject
        print('q made:',delta(start),'seconds')
        self.result = self.model.objects.filter(self.q)
        print('filtering with q:',delta(start),'seconds')
        self.check_completeness_approval()
        print('check completeness approval:',delta(start),'seconds')
        self.set_ordering_and_direction()
        print('ordering direction:',delta(start),'seconds')
        #self.exclude_doubles() 
        # returns a list of unique instances, 
        # commented out because it is very slow
        if 'empty' in self.query.special_terms:
            print('selecting empty fields in fields:',self.active_fields)
            self.select_empty() 
        print('empty selection:',delta(start),'seconds')
        self.nentries_found = self.result.count()
        print('counting entries:',delta(start),'seconds')
        self.nentries = '# Entries: ' + str(self.nentries_found) 
        if self.max_entries:
            if self.nentries_found > self.max_entries:
                self.nentries += ' (truncated at '  
                self.nentries +=  str(self.max_entries) + ' entries)'
            temp =self.result[:self.max_entries]
            print('selecting max entries:',delta(start),'seconds')
        else: temp = self.result
        print('filtering took:',delta(start),'seconds')
        return temp

    @property
    def n(self):
        print(self.notes)



class Query:
    '''class to parse a http request extract query and extract relevant 
    information.'''
    def __init__(self,request=None, model_name='',query='', active_fields = None,
        special_terms = None):
        '''individual words and special terms are extracted from the query.
        a clean version of the query (without special terms) is constructed.
        $   symbol prepended to field names / can also be set by active_fields
        *   symbol prepended to special terms such as and/or / can also be set by
            special_terms 
        '''
        if query:
            self.query = query
        else:
            self.order = Order(request,model_name)
            self.query = self.order.query
        self.query_words = self.query.split(' ')
        self.words = self.query_words
        self.query_terms = [w for w in self.words if w and w[0] not in ['*','$']]
        self.clean_query = ' '.join(self.query_terms)
        self.extract_field_names()
        #set the fields and special terms provided in the 
        #active_fields & special_terms
        #i.e. not in the query itself
        if active_fields and type(active_fields) == list:
            self.fields.extend(active_fields)
        self.extract_special_terms(special_terms)
        if not query and not active_fields and not special_terms:
            self.empty = True
        else: self.empty = False
    

    def extract_field_names(self):
        '''set the fields that should be active for the search
        if none are set all fields are active except the default 
        excluded ones e.g. id
        '''
        temp= [w[1:] for w in self.words if len(w) > 1 and w[0] == '$']
        self.field_term, self.fields= [],[]
        for term in temp:
            if ':' in term:self.field_term.append(term.split(':'))
            else: self.fields.append(term.lower())

    def extract_special_terms(self,special_terms):
        '''set the special terms that should active for the search
        '''
         
        x = [w[1:].lower() for w in self.words if len(w) > 1 and w[0] == '*']
        self.special_terms = x
        if special_terms and type(special_terms) == list:
            self.special_terms.extend(special_terms)
        self.completeness,self.approval,self.incompleteness = None, None, None
        if 'complete' in self.special_terms: self.completeness = True
        elif 'incomplete' in self.special_terms: self.completeness = False
        if 'not approved' in self.special_terms:
            self.approval = False
            self.completeness = True
        elif 'issue' in self.special_terms:
            self.incompleteness = True
        st = self.special_terms
        if 'combine' in st or 'combine words' in st:
            self.combine = True
        else: self.combine = False
        if 'exact' in self.special_terms:self.option ='iexact'
        else: self.option = 'icontains'
            
    
            
class Field:
    def __init__(self,name,description):
        '''representation of a field on a django model
        name            the name of the field on the model  e.g. name or title
        description     djangos description of a field to set the field type
                        this allows for the exclusion of certain fields because 
                        you cannot filter on them
                        
        '''
        self.name = name
        self.description = description
        self.set_field_type()
        self.set_include()
        self.check_relation()

    def __repr__(self):
        return self.name

    def set_include(self, value = None):
        '''sets whether the field should be used for searching
        only used if one ore more fields are specified otherwise all fields
        are used that are not excluded by default, such as id
        value       set include to be true or false
        '''
        self.include = True 
        self.exclude = False
        exclude = 'id,gps,gps_names,source_link,publisher_names,identifier,year'
        exclude += ',group_tags,relations,copyright,loc_ids,connection_count'
        exclude += ',setting_location_pks,publication_location_pks'
        exclude += ',publication_years'
        exclude = exclude.split(',')
        if self.name in exclude or self.bool or self.file or self.image: 
            self.include = False 
            self.exclude = True
        if value != None and value in [True,False]: self.include = value


    def set_field_type(self):
        '''sets booleans for field types (see field_typedict).'''
        ftd = get_field_typesdict()
        for name in ftd.keys():
            v= True if name in self.description else False
            setattr(self,ftd[name],v)

    def check_relation(self):
        '''checks whether a field is a foreign key or m2m and creates the 
        full name
        variable to end up with a field to be filtered on 
        (whether it is a relational
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
    def __init__(self,request=None, model_name=None,order=''):
        '''get the order and direction from the request and set it in such a 
        way that it can be used in a filter call.
        '''
        if order:
            self.order_by = order
            self.direction = 'ascending'
            self.order_results = True if order else False
        else:
            self.request = request
            self.model_name = model_name
            self.set_values()
            self.order_results = True if request else False

    def set_values(self):
        if self.request:
            temp = self.request.GET.get('order_by')
            tquery = self.request.GET.get('query')
            if temp: 
                order_by,old_order,old_direction,tquery = temp.split(',')
                if order_by == old_order:
                    direction = 'descending' if old_direction == 'ascending' else 'ascending'
                elif order_by =='connection_count':direction = 'descending'
                else: direction = 'ascending'
            else: 
                order_by = get_foreign_keydict()[self.model_name.lower()]
                direction = 'ascending'
        else: 
            tquery, order_by, direction = None, None, None
            
        if tquery == None: query = ''
        else: query =tquery

        self.order_by = order_by
        self.query = query
        self.direction = direction

    def __repr__(self):
        return str(self.order_by) + ', ' + str(self.direction)


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
    '''for foreignkey fields, map the model name to the field to search on
    e.g. for publication search on the field title: publication__title
    '''
    m = 'publication:title,text:title,illustration:caption'
    m += ',publisher:name,location:name'
    m += ',person:first_name,movement:name,periodical:title,language:name'
    m += ',genre:name'
    m += ',category:name,movement_type:name,form:name,userloc:name,loc_type:name'
    m += ',geoloc:name,style:name,figure:name,birth_place:name,death_place:name'
    return make_dict(m)


def delta(start):
    return time.time() - start

def filter_on_list(instance_dict, filter_list):
    instances = []
    for key,inst in instance_dict.items():
        if key in filter_list:
            for instance in inst:
                if instance not in instances: instances.append(instance)
    return instances

def _instance2identifier_dict(d):
    o = {}
    for key,instances in d.items():
        o[key] = [x.identifier for x in instances]
    o['all'] = []
    for ids in o.values():
        o['all'].extend(ids)
    return o

        
