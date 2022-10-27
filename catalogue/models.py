from django.db import models
from django.conf import settings
from django.utils import timezone
from django import urls
import glob
from locations.models import Location
from utilities.models import Language, RelationModel, SimpleModel 
from utilities.models import GroupTag
from utils.model_util import id_generator, info,instance2names
from utils.model_util import get_empty_fields
from utils.map_util import field2locations, pop_up, get_location_name,gps2latlng
from utils.cleanup_filenames import remove_diacritics_filename
import os
from partial_date import PartialDateField
import time

def make_simple_model(name):
    '''creates a new model based on name, 
    uses the abstract class SimpleModel.
    '''
    exec('class '+name + '(SimpleModel,info):\n\tpass',globals())

names = 'CopyRight,Genre,TextType,TextTextRelationType,Audience'
names += ',PublicationType,IllustrationCategory'
names += ',IllustrationIllustrationRelationType,IllustrationType,UsePermission'
names = names.split(',')

for name in names:
    make_simple_model(name)
            

class Item(models.Model):
    '''abstract model for non simple/ non relational catalogue models.
    sets fields that are used by most models and defines methods used by 
    most models
    '''
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    description = models.TextField(blank=True)
    notes = models.TextField(default='',blank=True, null=True)
    complete = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    incomplete = models.BooleanField(default=False)
    source_link= models.CharField(max_length=1000,blank=True,null=True)
    copyright = models.ForeignKey(CopyRight,**dargs)
    gps = models.CharField(max_length=300,default ='')
    gps_names = models.CharField(max_length=4000,default='')
    loc_ids = models.CharField(max_length=300,default ='')
    group_tags= models.ManyToManyField(GroupTag,blank=True, default= None)
    location_field = 'location'
    connection_count = models.PositiveIntegerField(null=True,blank=True) 
    
    def __str__(self):
        return self.instance_name

    def _set_connection_count(self):
        from utils import instance_links
        links = instance_links.Links(self)
        self.connection_count = links.n_connections
        self.save()

    def save(self,*args,**kwargs):
        '''sets the gps coordinates and names field after saving based 
        on the fk location
        '''
        super(Item,self).save(*args,**kwargs)
        old_gps = self.gps
        self._set_gps()
        if self.gps != old_gps:super(Item,self).save()
        super(Item,self).save(*args,**kwargs)

    @property
    def edit_url(self):
        return self._meta.app_label + ':edit_' + self._meta.model_name

    @property
    def detail_url(self):
        return self._meta.app_label + ':detail_' + self._meta.model_name

    def _set_gps(self):
        '''sets the gps coordinates and name of related location to speed 
        up map visualization.
        '''
        locations = field2locations(self,self.location_field)
        self.loc_ids = ''
        if locations:
            gps = ' | '.join([l.gps for l in locations if l.gps])
            names= ' | '.join([l.name for l in locations if l.gps])
            ids = ','.join([str(l.pk) for l in locations])
            self.gps = gps
            self.gps_names = names
            self.loc_ids = ids
        if hasattr(self,'setting_location_pks'):
            ids = self.get_setting_location_pks + self.get_publication_location_pks
            if self.loc_ids:
                ids += self.loc_ids.split(',')
            if ids:
                ids = list(set(map(str,ids)))
                self.loc_ids = ','.join(ids)
        else: self.gps, self.gps_names, self.loc_ids = '','',''

    def empty_fields(self,fields = []):
        return get_empty_fields(self,fields, default_is_empty = True)

    @property
    def latlng(self):
        return gps2latlng(self.gps)

    @property
    def latlng_names(self):
        try: return self.gps_names.split(' - ')
        except: return None

    @property
    def location_string(self):
        try:return ', '.join(self.latlng_names)
        except: return ''

    def pop_up(self, latlng=None):
        '''creates html for the pop up for map visualization.'''
        return pop_up(self,latlng)  

    @property
    def instance_name(self):
        if hasattr(self,'title_exact'):
            return self.title
        if hasattr(self,'title'):
            return self.title
        if hasattr(self,'name'):
            return self.name
        if hasattr(self,'caption'):
            return self.caption
        else: 
            m = 'please override instance_name property with '
            m += 'correct "name" field'
            raise ValueError(m)

    def plot(self):
        '''provides information to plot an instance on the map'''
        app_name, model_name = instance2names(self) 
        gps = str(self.gps.split(' | ')).replace("'",'')
        d = {'app_name':app_name, 'model_name':model_name, 
            'gps':gps, 'pk':self.pk}
        return d

    def latlng2name(self,latlng):
        return get_location_name(self,latlng)

    @property
    def identifier(self):
        i = self._meta.app_label + '_' + self._meta.model_name 
        i += '_' + str( self.pk )
        return i

    class Meta:
        abstract = True

    @property
    def sidebar_info(self):
        start = time.time()
        d = {}
        d['name'] = self.instance_name
        if self._meta.model_name in ['text','publication']: 
            if not self.language: d['language'] = ''
            d['language'] = self.language.name 
        if self._meta.model_name == 'publication':
            if not self.form: d['publication_type'] = ''
            d['publication_type'] += self.form.name
        d['years'] = self.get_years
        d['detail_url'] = urls.reverse_lazy(self.detail_url, args = [self.pk])
        if hasattr(self,'type_info'):d['extra'] = self.type_info
        else: d['extra'] = ''
        d['identifier'] = self.identifier
        if hasattr(self,'setting_location_pks'):
            d['setting_location_pks']= self.get_setting_location_pks
            d['publication_location_pks']= self.get_publication_location_pks
        return d



# --- non simple / non relational catalogue models ---

class Text(Item, info):
    '''a text can be an entire book or article or a subsection thereof.'''
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    title = models.CharField(max_length=300)
    setting = models.CharField(max_length=300,blank=True)
    language = models.ForeignKey(Language, **dargs)
    genre = models.ForeignKey(Genre, **dargs)
    text_type = models.ForeignKey(TextType, **dargs)
    relations = models.ManyToManyField('self',
        through='TextTextRelation',symmetrical=False, default=None)
    location= models.ManyToManyField(Location,blank=True, default= None)
    person = models.CharField(max_length=2000,blank=True,null=True)
    setting_location_pks = models.CharField(max_length = 600, blank=True,null=True)
    publication_location_pks = models.CharField(max_length = 600, blank=True,null=True)
    publication_years = models.CharField(max_length = 600, blank = True, null=True)
    language_name = model.CharField(max_length(50, blank=True,null=True)

    def _set_language_name(self):
        if self.language: self.language_name = self.language.name
        else: self.language_name = ''
        self.save()

    def _set_person(self):
        names = [] 
        for ptr in self.persontextrelation_set.all():
            names.append(ptr.person.full_name)
        self.person = '; '.join(names)
        self.save()

    @property
    def get_setting_location_pks(self):
        if self.setting_location_pks == None: return [] 
        if self.setting_location_pks == '': return []
        return list(map(int,self.setting_location_pks.split(',')))

    @property
    def get_publication_location_pks(self):
        if self.publication_location_pks == None: return [] 
        if self.publication_location_pks == '': return []
        return list(map(int,self.publication_location_pks.split(',')))

    def _set_setting_location_pks(self):
        '''return location pk for the setting of the text (place text is situated).'''
        locations = self.location.all()
        pks = []
        for location in locations:
            if location.pk not in pks: pks.append(location.pk)
        self.setting_location_pks = ','.join(map(str,pks))
        self.save()

    def _set_publication_location_pks(self):
        '''return location pk for publication of the text.'''
        pks = []
        for publication in self.publications:
            publication._set_publication_location_pks()
            for pk in publication.get_publication_location_pks:
                if pk not in pks: pks.append(pk)
        self.publication_location_pks = ','.join(map(str,pks))
        self.save()

            
    class Meta:
        unique_together = 'title,setting,language'.split(',')

    def latlng2name(self,latlng):
        location_name = super().latlng2name(latlng)
        if location_name:
            return 'Text situated in <b>' +location_name + '</b>'
        else: return '<p></p>'

    def pop_up(self,latlng):
        m = ''
        if self.language: 
            m += '<p><small>language <b>' + self.language.name 
        if self.language and self.genre: m += '</b>, '
        else: m += '</b></small></p>'
        if not m and self.genre: m += '<p><small>'
        if self.genre: 
            m += 'genre <b>' + self.genre.name + '</b></small></p>'
        return pop_up(self,latlng,extra_information=m)

    @property
    def persons(self):
        if hasattr(self,'_persons'): return self._persons
        self._persons = []
        ptrs = self.persontextrelation_set.all()
        for ptr in ptrs:
            self._persons.append(ptr.person)
        return self._persons

    @property
    def genders(self):
        'return list of genders of persons linked to this text.'
        return list(set([x.sex for x in self.persons]))

    @property
    def get_years(self):
        if self.publication_years== None: return [] 
        if self.publication_years== '': return []
        return list(map(int,self.publication_years.split(',')))
        

    def _set_publication_years(self):
        dates = self.get_dates
        years = [str(date.year) for date in dates]
        self.publication_years = ','.join(years)
        self.save()

    @property
    def get_dates(self):
        '''text object does not contain date, 
        only the linked publication has a date.
        a text can have multiple dates (if it is linked to 
        multiple publications)
        the date is the date of publication of the publication instance
        returns a list of partialdate objects
        '''
        if hasattr(self,'_dates'): return self._dates
        tpr =  self.textpublicationrelation_set.all()
        if not tpr: return ''
        o = []
        for x in tpr:
            if not hasattr(x,'publication'): continue
            date = x.publication.date
            if date: o.append(date)
        self._dates = o
        return o

    @property
    def dates(self):
        dates = self.get_dates
        if not dates: return ''
        output = []
        o = 'Published in: '
        for i,date in enumerate(dates):
            o += str(date.year) 
            if i != len(dates) -1:o += ', '
        return o

    @property
    def roles_to_persons_dict(self):
        if hasattr(self,'_roles_to_persons_dict'): return self._roles_to_persons_dict
        d ={}
        ptrs = self.persontextrelation_set.all()
        for ptr in ptrs:
            if ptr.role.name not in d.keys(): d[ptr.role.name] = []
            d[ptr.role.name].append(ptr.person)
        self._roles_to_persons_dict = d
        return self._roles_to_persons_dict

    @property
    def publications(self):
        tpr =  self.textpublicationrelation_set.all()
        if not tpr: return ''
        o = []
        for x in tpr:
            o.append( x.publication )
        o = sorted(o, key = lambda x: x.date)
        return o

    @property
    def type_info(self):
        if self.text_type: return self.text_type.name
        return '' 

    @property
    def reviews(self):
        if hasattr(self,'_reviews'): return self._reviews
        d = {'reviews':[]}
        trp = self.textreviewpublicationrelation_set.all()
        reviews = [x.publication for x in trp]
        if self.text_type and self.text_type.name.lower() == 'review' or reviews: 
            d['type'] = 'review of'
        else: d['type'] = 'reviewed by'
        reviews.extend(self.get_linked_texts('review'))
        for review in reviews:
            d['reviews'].append(review)
        if len(reviews) == 0: d = {}
        self._reviews = d
        return self._reviews

    @property
    def type_to_linked_texts_dict(self):
        if hasattr(self,'_linked_texts'): return self._linked_texts
        relation_types = TextTextRelationType.objects.all()
        d = {}
        for t in relation_types:
            if t.name.lower() == 'review': continue
            texts =  self.get_linked_texts(t.name)
            if texts: 
                d[t.name.lower()] = self.get_linked_texts(t.name)
        self._linked_texts = d
        return self._linked_texts

        
    def get_linked_texts(self, relation_type):
        output = []
        ttr = self.secondary.filter(relation_type__name__icontains = relation_type)
        output.extend([x.primary for x in ttr])
        ttr = self.primary.filter(relation_type__name__icontains = relation_type)
        output.extend([x.secondary for x in ttr])
        return output

    @property
    def authors(self):
        d = self.roles_to_persons_dict
        if 'author' in d.keys(): return d['author']
        else: return []


def make_filename(instance, filename):
    '''creates a filename for uploaded images'''
    app_name, model_name = instance2names(instance)
    name,ext = os.path.splitext(filename)
    name += '_django-'+time.strftime('%y-%m-%d-%H-%M') + ext
    pn = model_name.lower() +'/'+ name
    pn = remove_diacritics_filename(pn)
    return pn

class Illustration(Item, info):
    '''a illustration typically part of publication'''
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    caption =  models.CharField(max_length=300,null=True,blank=True)
    category = models.ForeignKey(IllustrationCategory,
        on_delete=models.SET_NULL,
        blank=True,null=True,related_name='Illustration')
    categories=models.ManyToManyField(IllustrationCategory,blank=True,
        related_name='Illustrations') 
    page_number = models.CharField(max_length=50, default = '', blank=True)
    upload= models.ImageField(upload_to=make_filename,null=True,blank=True)
    relations = models.ManyToManyField('self',
        through='IllustrationIllustrationRelation',symmetrical=False, 
        default=None)
    illustration_type = models.ForeignKey(IllustrationType, **dargs)
    location= models.ManyToManyField(Location,blank=True, default= None)
    setting = models.CharField(max_length=300,blank=True)
    location_field = 'location'
    image_filename = models.CharField(max_length=500,default='',blank=True,
        null=True)
    person = models.CharField(max_length=2000,blank=True,null=True)
    use_permission= models.ForeignKey(UsePermission,on_delete=models.SET_NULL,
        null=True)
    setting_location_pks = models.CharField(max_length=600,blank=True,null=True)
    publication_location_pks = models.CharField(max_length=600,blank=True,null=True)
    publication_years = models.CharField(max_length=600,blank=True,null=True)

    @property
    def get_setting_location_pks(self):
        if self.setting_location_pks == None: return [] 
        if self.setting_location_pks == '': return [] 
        return list(map(int,self.setting_location_pks.split(',')))

    @property
    def get_publication_location_pks(self):
        if self.publication_location_pks == None: return [] 
        if self.publication_location_pks == '': return [] 
        return list(map(int,self.publication_location_pks.split(',')))

    def _set_setting_location_pks(self):
        '''return location pk for the setting of the illustration 
        (place text is situated).
        '''
        locations = self.location.all()
        pks = []
        for location in locations:
            if location.pk not in pks: pks.append(location.pk)
        self.setting_location_pks = ','.join(map(str,pks))
        self.save()

    def _set_publication_location_pks(self):
        '''return location pk for publication of the text.'''
        pks = []
        for publication in self.publications:
            publication._set_publication_location_pks()
            for pk in publication.get_publication_location_pks:
                if pk not in pks: pks.append(pk)
        self.publication_location_pks = ','.join(map(str,pks))
        self.save()

    def _set_person(self):
        names = [] 
        for pir in self.personillustrationrelation_set.all():
            names.append(pir.person.full_name)
        self.person = '; '.join(names)
        self.save()

    @property
    def persons(self):
        if hasattr(self,'_persons'): return self._persons
        self._persons = []
        pirs = self.personillustrationrelation_set.all()
        for pir in pirs:
            self._persons.append(pir.person)
        return self._persons

    @property
    def genders(self):
        'return list of genders of persons linked to this illustration.'
        return list(set([x.sex for x in self.persons]))

    @property
    def roles_to_persons_dict(self):
        d ={}
        pirs = self.personillustrationrelation_set.all()
        for pir in pirs:
            if pir.role.name not in d.keys(): d[pir.role.name] = []
            d[pir.role.name].append(pir.person)
        return d


    class Meta:
        unique_together = 'caption,image_filename,page_number'.split(',')

    @property
    def type_info(self):
        if self.category: return self.category.name
        return '' 

    @property
    def publications(self):
        tpr =  self.illustrationpublicationrelation_set.all()
        if not tpr: return ''
        o = []
        for x in tpr:
            o.append( x.publication )
        o = sorted(o, key = lambda x: x.date)
        return o

    @property
    def get_years(self):
        if self.publication_years== None: return [] 
        if self.publication_years== '': return []
        return list(map(int,self.publication_years.split(',')))
        

    def _set_publication_years(self):
        dates = self.get_dates
        years = [str(date.year) for date in dates]
        self.publication_years = ','.join(years)
        self.save()

    @property
    def get_dates(self):
        '''illustration object does not contain date, 
        only the linked publication has a date.
        a illustration can have multiple dates 
        (if it is linked to multiple publications)
        the date is the date of publication of the publication instance
        returns a list of partialdate objects
        '''
        if hasattr(self,'_dates'): return self._dates
        publications = self.publications
        if not publications: return ''
        o = []
        for x in publications:
            date = x.date
            if date: o.append(date)
        self._dates = o
        return o

    @property
    def dates(self):
        dates = self.get_dates
        if not dates: return ''
        o = 'Published in: '
        for date in dates:
            o += str(date.year) + ' '
        return o

    

class Publisher(Item, info):
    '''Company that publishes works.'''
    name = models.CharField(max_length=300, unique=True)
    location= models.ManyToManyField(Location,blank=True,default=None)
    founded = models.PositiveIntegerField(null=True,blank=True) 
    closure = models.PositiveIntegerField(null=True,blank=True) 
    person = models.CharField(max_length=2000,blank=True,null=True)

    def _set_person(self):
        names = [] 
        for p in self.publisher.all():
            names.append(p.manager.full_name)
        self.person = '; '.join(names)
        self.save()

    class Meta:
        ordering = ['name']
        unique_together = 'name,founded'.split(',')

    @property
    def get_years(self):
        if not self.founded: return []
        return [self.founded]

    @property
    def get_dates(self):
        if not self.founded: return ''
        return [self.founded]

    @property
    def dates(self):
        o =''
        if self.founded: o += 'founded in: ' +str(self.founded) + ' '
        if self.closure: o += 'closure in: ' +str(self.closure)
        return o

    @property
    def location_names(self):
        o = []
        for l in self.location.all():
            o.append(l.full_name)
        return ' | '.join(o)

    @property
    def persons(self):
        if hasattr(self,'_persons'):return self._persons
        o = []
        for publisher_manager_relation in self.publisher.all():
            o.append(publisher_manager_relation.manager)
        self._persons = o
        return self._persons
    
    @property
    def publications(self):
        if hasattr(self,'_publications'): return self._publications
        output = []
        for publication in self.publication_set.all():
            output.append(publication)          
        self._publications = sorted(output, key = lambda x: x.date)
        return self._publications
            

    def pop_up(self,latlng):
        m = ''
        if self.founded: m += '<p><small>founded <b>' + str(self.founded)
        if self.founded and self.closure: m += '</b>, '
        else: m += '</b></small></p>'
        if not m and self.founded: m += '<p><small>'
        if self.closure: 
            m += 'closure <b>' + str(self.closure) + '</b></small></p>'
        return pop_up(self,latlng,extra_information=m)


class Publication(Item, info):
    '''The publication of a text or collection of texts and illustrations'''
    title = models.CharField(max_length=300,null=True)
    publisher = models.ManyToManyField(Publisher,blank=True)
    form = models.ForeignKey(PublicationType,on_delete=models.SET_NULL,
        null=True)
    issue = models.PositiveIntegerField(default=0,blank=True) 
    volume = models.PositiveIntegerField(default=0,blank=True) 
    # obsolete, replace by date
    year = models.PositiveIntegerField(null=True,blank=True) 
    date = PartialDateField(null=True,blank=True)
    location = models.ManyToManyField(Location,blank=True,default=None) 
    pdf = models.FileField(upload_to='publication/',null=True,blank=True) # ?
    cover = models.ImageField(upload_to='publication/',null=True,blank=True)
    publisher_names = models.CharField(max_length = 500, null=True,
        blank=True,default='')
    use_permission= models.ForeignKey(UsePermission,on_delete=models.SET_NULL,
        null=True)
    setting_location_pks = models.CharField(max_length = 600, blank=True,null=True)
    publication_location_pks = models.CharField(max_length = 600, blank=True,null=True)
    language_names = model.CharField(max_length(50, blank=True,null=True)
    language_names = model.CharField(max_length(90, blank=True,null=True)

    def _set_language_names(self):
        languages = self.languages
        if languages: self.language_names = languages
        self.save()

    def _set_form_name(self):

    def get_language_names(self):
        return self.language_names.split(',')

    def pop_up(self,latlng):
        m = ''
        if self.publisher_names: 
            m += '<p><small>published by <b>'+self.publisher_names
            m +='</b></small></p>'
        if self.volume: m+='<p><small>volume <b>' + str(self.volume)
        if not self.issue: m+= '</b></small></p>'
        if not self.volume and self.issue:m+= '<p><small>'
        if self.issue and self.volume: m += '</b>, '
        if self.issue: m += 'issue <b>'+ str(self.issue) +'</b></small></p>'
        if self.date: 
            m+='<p><small>published in <b>'+ self.date.name+'</b></small></p>'
        return pop_up(self,latlng,extra_information=m)

    @property
    def type_info(self):
        if self.category: return self.form.name
        return '' 

    class Meta:
        unique_together=[['title','publisher_names','date','issue','volume']]

    @property
    def persons(self):
        if hasattr(self,'_persons'): return self._persons
        self._persons = []
        for text_dict in self.texts:
            text = text_dict['text']
            if len(text.persons) > 0:
                self._persons.extend(text.persons)
        for illustration_dict in self.illustrations:
            illustration = illustration_dict['illustration']
            if len(illustration.persons) > 0:
                self._persons.extend(illustration.persons)
        self._persons = list(set(self._persons))
        return self._persons

    @property
    def genders(self):
        'return list of genders of persons linked to this publication.'
        return list(set([x.sex for x in self.persons]))

    @property
    def get_setting_location_pks(self):
        if self.setting_location_pks == None: return [] 
        if self.setting_location_pks == '': return [] 
        return list(map(int,self.setting_location_pks.split(',')))

    @property
    def get_publication_location_pks(self):
        if self.publication_location_pks == None: return [] 
        if self.publication_location_pks == '': return [] 
        return list(map(int,self.publication_location_pks.split(',')))

    def _set_setting_location_pks(self):
        '''return location pk for the setting of the text (place text is situated).'''
        pks = []
        for text_dict in self.texts:
            text = text_dict['text']
            text._set_setting_location_pks()
            for pk in text.get_setting_location_pks:
                if not pk: continue
                if pk not in pks: pks.append(pk)
        for illustration_dict in self.illustrations:
            illustration = illustration_dict['illustration']
            illustration._set_setting_location_pks()
            for pk in illustration.get_setting_location_pks:
                if not pk: continue
                if pk not in pks: pks.append(pk)
        self.setting_location_pks = ','.join(map(str,pks))
        self.save()

    def _set_publication_location_pks(self):
        '''return location pk for publication of the publication.'''
        locations = self.location.all()
        pks = []
        for location in locations:
            if location.pk not in pks: pks.append(location.pk)
        self.publication_location_pks = ','.join(map(str,pks))
        self.save()


    @property
    def publisher_str(self):
        return ' | '.join([x.name for x in self.publisher.all()])
        # return self.publisher_names

    @property
    def location_str(self):
        return ' | '.join([pu.name for pu in self.location.all()])

    @property
    def location_names(self):
        o = []
        for l in self.location.all():
            o.append(l.full_name)
        return ' | '.join(o)

    @property
    def get_years(self):
        if not self.date: return []
        return [self.date.year]

    @property
    def get_dates(self):
        if not self.date: return ''
        return [self.date]

    @property
    def dates(self):
        dates = self.get_dates
        if not dates: return ''
        o = 'Published in: '
        for date in dates:
            o += str(date.year) + ' '
        return o

    @property
    def title_exact(self):
        m = self.title
        add_bracket = False
        if self.date or self.issue or self.volume: 
            m += ' ('
            add_bracket = True
        if self.volume: m += 'vol. ' +str(self.volume) 
        if (self.volume and self.issue) or (self.volume and self.date):
            m += ', '
        if self.issue: m += 'n. ' + str(self.issue)
        if self.issue and self.date:m += ', '
        if self.date: m += self.date.pretty_string() 
        if add_bracket: m +=')'
        return m

    @property
    def illustrations(self):
        output = []
        ipr = self.illustrationpublicationrelation_set.all()
        if not ipr: return output
        for x in ipr:
            d = {}
            try: order = int(x.page)
            except: order = 0
            d['order'] = order
            d['page'] = x.page
            if x.illustration.upload: d['url_image'] = x.illustration.upload.url
            else:d['url_image'] = ''
            d['caption'] = x.illustration.caption
            d['detail_url'] = x.illustration.detail_url
            d['pk'] = x.illustration.pk
            d['illustration'] = x.illustration
            output.append(d)
        return sorted(output, key=lambda x: x['order'])

    @property
    def texts(self):
        if hasattr(self,'_texts'): return self._texts
        output = []
        tpr = self.textpublicationrelation_set.all()
        if not tpr:return output
        for x in tpr:
            d ={}
            try: order = int(x.start_page)
            except: order = 0
            d['order'] = order
            d['start_page'] = x.start_page
            d['end_page'] = x.end_page
            d['title'] = x.text.title
            d['detail_url'] = x.text.detail_url
            d['pk'] = x.text.pk
            d['authors'] = x.text.authors
            d['text'] = x.text
            if x.text.language: d['language'] = x.text.language.name
            else: d['language'] = ''
            if x.text.text_type: d['text_type'] = x.text.text_type.name
            else: d['text_type'] = ''
            if 'translator' in x.text.roles_to_persons_dict.keys():
                d['translators'] = x.text.roles_to_persons_dict['translator']
            else: d['translators'] = []
            if x.text.genre: d['genre'] = x.text.genre.name
            else: d['genre'] = ''
            output.append(d)
        self._texts = sorted(output, key=lambda x: x['order'])
        return self._texts

    @property
    def text_types(self):
        if hasattr(self,'_text_types'): return self._text_types
        temp = []
        for text_dict in self.texts:
            if text_dict['text_type'] == '':
                if 'original' not in temp:temp.append('original')
            elif text_dict['text_type'] not in temp: 
                temp.append(text_dict['text_type'])
        self._text_types = temp
        return self._text_types

    @property
    def languages(self):
        if hasattr(self,'_languages'): return self._languages
        temp = []
        for text_dict in self.texts:
            if text_dict['language'] == '': continue
            if text_dict['language'] not in temp:
                temp.append(text_dict['language'])
        self._languages = temp
        return self._languages

    @property
    def genres(self):
        if hasattr(self,'_genres'): return self._genres
        temp = []
        for text_dict in self.texts:
            if text_dict['genre'] == '': continue
            if text_dict['genre'] not in temp:
                temp.append(text_dict['genre'])
        self._genres = temp
        return self._genres

    @property
    def publishers(self):
        if hasattr(self,'_publishers'): return self._publishers
        o = []
        for publisher in self.publisher.all():
            o.append(publisher)
        self._publishers = o
        return self._publishers

    @property
    def authors(self):
        if hasattr(self,'_authors'): return self._authors
        output = []
        for text in self.texts:
            if text['authors']: output.extend(text['authors'])
        self._authors = list(set(output))
        return self._authors

    @property
    def translators(self):
        if hasattr(self,'_translators'): return self._translators
        output = []
        for text in self.texts:
            if text['translators']: output.extend(text['translators'])
        self._translators= list(set(output))
        return self._translators
        
    @property
    def reviews(self):
        if hasattr(self,'_reviews'): return self._reviews
        o = []
        for tpr in self.textreviewpublicationrelation_set.all():
            o.append(tpr.text)
        self._reviews= o
        return self._reviews
        

        
class Periodical(Item, info):
    '''Recurrent publication.'''
    title = models.CharField(max_length=300)
    founded = models.PositiveIntegerField(null=True,blank=True) 
    closure = models.PositiveIntegerField(null=True,blank=True) 
    location= models.ManyToManyField(Location,blank=True,default =None)
    person = models.CharField(max_length=2000,blank=True,null=True)

    def _set_person(self):
        names = [] 
        for ppr in self.personperiodicalrelation_set.all():
            names.append(ppr.person.full_name)
        self.person = '; '.join(names)
        self.save()

    class Meta:
        unique_together = 'title,founded'.split(',')

    def pop_up(self,latlng):
        m = ''
        if self.founded: m += '<p><small>founded <b>' + str(self.founded)
        if self.founded and self.closure: m += '</b>, '
        else: m += '</b></small></p>'
        if not m and self.founded: m += '<p><small>'
        if self.closure: 
            m += 'closure <b>' + str(self.closure) + '</b></small></p>'
        x = self.periodicalpublicationrelation_set.all()
        n=' | '.join(list(set([y.publication.publisher_names for y in x])))
        names = n
        if names: 
            m += '<p><small>published by <b>' + names + '</b></small></p>'
        return pop_up(self,latlng,extra_information=m)

    @property
    def location_names(self):
        o = []
        for l in self.location.all():
            o.append(l.full_name)
        return ' | '.join(o)

    @property
    def publications(self):
        if hasattr(self,'_publications'): return self._publications
        output = []
        for ppr in self.periodicalpublicationrelation_set.all():
            output.append(ppr.publication)          
        self._publications = sorted(output, key = lambda x: x.date)
        return self._publications

    @property
    def roles_to_persons_dict(self):
        if hasattr(self,'_role_person_dict'): return self._role_person_dict
        d ={}
        pprs = self.personperiodicalrelation_set.all()
        for ppr in pprs:
            if ppr.role.name.lower() not in d.keys(): d[ppr.role.name.lower()] = []
            d[ppr.role.name.lower()].append(ppr.person)
        self._role_person_dict = d
        return self._role_person_dict

    @property
    def get_years(self):
        if not self.founded: return []
        return [self.founded]

    @property
    def get_dates(self):
        if not self.founded: return ''
        return [self.founded]

    @property
    def dates(self):
        o =''
        if self.founded: o += 'founded in: ' +str(self.founded) + ' '
        if self.closure: o += 'closure in: ' +str(self.closure)
        return o

# ---- relation objects, e.g text publication relation etc. ----

class TextPublicationRelation(RelationModel): 
    '''Links a text with a publication.'''
    text = models.ForeignKey(Text, on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    start_page = models.CharField(max_length=5,null=True,blank=True)
    end_page = models.CharField(max_length=5,null=True,blank=True)
    model_fields = ['text','publication']

    def __str__(self):
        try:
            m =  self.text.title+ ' is a part of '
            m += self.publication.title
            return m
        except:
            print('textpublicationrelation name could not be made')
            return ''

    @property
    def primary(self):
        return self.text
        

class TextReviewPublicationRelation(RelationModel): 
    '''Links a review text with a publication.'''
    text = models.ForeignKey(Text, on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    model_fields = ['text','publication']

    def __str__(self):
        m =  self.text.title+ ' is a review of '
        m += self.publication.title
        return m

    @property
    def primary(self):
        return self.text


class IllustrationPublicationRelation(RelationModel): 
    '''Links a illustration with a publication.'''
    illustration = models.ForeignKey(Illustration, on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    page = models.CharField(max_length=5,null=True,blank=True)
    model_fields = ['illustration','publication']

    def __str__(self):
        m =  self.illustration.caption+ ' is a part of '
        m += self.publication.title
        return m

    @property
    def primary(self):
        return self.illustration


class PeriodicalPublicationRelation(RelationModel, info):
    '''linking a periodical to a publication 
    (a specific issue of a periodical).'''
    periodical= models.ForeignKey(Periodical, on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    volume= models.PositiveIntegerField(null=True,blank=True)
    issue= models.PositiveIntegerField(null=True,blank=True)
    model_fields = ['periodical','publication']

    def __str__(self):
        m =  self.periodical.title+ ' is a periodical in '
        m += self.publication.title
        return m

    @property
    def primary(self):
        return self.periodical


class TextTextRelation(models.Model, info):
    '''connects two texts with a specific type of relation e.g. original 
    and translation (primary, secondary).'''
    primary = models.ForeignKey('Text', related_name='primary',
                                    on_delete=models.CASCADE, default=None)
    secondary = models.ForeignKey('Text', related_name='secondary',
                                    on_delete=models.CASCADE, default=None)
    relation_type = models.ForeignKey(TextTextRelationType, 
                                    on_delete=models.CASCADE, default=None)
    model_fields = ['primary','secondary']

    def __str__(self):
        m =  self.relation_type.name +' relation between ' 
        m += self.secondary.title +' and '
        m += self.primary.title
        return m


class IllustrationIllustrationRelation(models.Model, info):
    '''connects two texts with a specific type of relation e.g. original 
    and translation (primary, secondary).'''
    primary = models.ForeignKey('Illustration', related_name='primary',
                                    on_delete=models.CASCADE, default=None)
    secondary = models.ForeignKey('Illustration', related_name='secondary',
                                    on_delete=models.CASCADE, default=None)
    relation_type = models.ForeignKey(IllustrationIllustrationRelationType, 
                                    on_delete=models.CASCADE, default=None)
    model_fields = ['primary','secondary']

    def __str__(self):
        try:
            m =  self.relation_type.name +' relation between ' 
            m += self.secondary.caption+' and '
            m += self.primary.caption
        except:
            m='WARNING, could not create string for '
            m+='IllustrationIllustrationRelation'
            print(m)
            return ''
        return m
