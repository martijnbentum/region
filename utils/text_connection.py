from django.core import serializers
from utils.map_util import get_all_location_ids_dict
import json

class text_connection:
    def __init__(self,text):
        self.start_text = text
        self.type = text.type_info
        self.is_translation = self.type == 'translation'
        self.is_review = self.type == 'review'
        self.get_original()
        self.collect_translations()
        self.collect_location_pks()
        self.set_locations()

    def collect_translations(self):
        original = self.original
        self.type_to_linked_texts_dict = original.type_to_linked_texts_dict
        texts = flatten_list_of_list(self.type_to_linked_texts_dict.values())
        self.all_texts = texts
        if original not in self.all_texts: self.all_texts.append(original)
        self.languages = list(set([x.language_name for x in self.all_texts]))

    def get_original(self):
        self.original = None
        self.is_original = not self.is_review and not self.is_translation 
        if self.is_original: self.original = self.start_text
        if self.is_translation: key = 'translation'
        if self.is_review: key = 'review'
        if not self.original:
            for text in self.start_text.type_to_linked_texts_dict[key]:
                if text.type_info != 'translation':
                    self.original = text
                    break
        self.has_original = self.original == None


    def collect_location_pks(self):
        self.publication_location_pks= []
        self.setting_location_pks = []
        self.author_location_pks = []
        temp = self.original.publication_location_pks
        self.original_publication_location_pks = list(map(int,temp.split(',')))
        for text in self.all_texts:
            pks = text.publication_location_pks.split(',')
            for pk in pks:
                if not pk: continue
                if pk not in self.publication_location_pks:
                    self.publication_location_pks.append(int(pk))
            pks = text.setting_location_pks.split(',')
            for pk in pks:
                if not pk: continue
                if pk not in self.setting_location_pks:
                    self.setting_location_pks.append(int(pk))
        for author in self.original.authors:
            temp = list(map(int,author.loc_ids.split(',')))
            self.author_location_pks.extend(temp) 
    
    def set_locations(self):
        instances = self.all_texts + self.original.authors
        self.locations = get_all_location_ids_dict(instances,
            add_names_gps=True)
        for location_pk, info in self.locations.items():
            info['location_type'] = []
            info['original'] = False
            if location_pk in self.publication_location_pks:
                info['location_type'].append('publication')
            if location_pk in self.setting_location_pks:
                info['location_type'].append('setting')
            if location_pk in self.original_publication_location_pks:
                info['original'] = True
            if location_pk in self.author_location_pks:
                info['location_type'].append('author')
        



    def to_dict(self):
        d = {}
        original = self.original
        td = self.type_to_linked_texts_dict
        d['original'] = instance_to_info_dict(original)
        if 'translation' in td.keys():
            d['translations'] = [instance_to_info_dict(x) for x in td['translation']]
        else: d['translations'] = []
        if 'review' in td.keys():
            d['reviews'] = [instance_to_info_dict(x) for x in td['review']]
        else: d['reviews'] = []
        d['titles'] = list(set([x.title for x in self.all_texts]))
        d['original_title'] = original.title if original else ''
        d['other_titles'] = [t for t in d['titles'] if t != original.title]
        d['languages'] = self.languages
        d['original_language'] = original.language_name if original else ''
        ol = d['original_language']
        d['other_languages'] = [l for l in self.languages if l != ol]
        author_names = ', '.join([x.name for x in original.authors])
        d['original_author'] = author_names if original else ''
        d['genre'] = original.genre.name
        d['locations'] = list(self.locations.values())
        self.d = d
        return d

def _get_author_name(instance):
    persons = []
    if instance.text_type == None or instance.text_type.name == 'original':
        relation_name = 'author'
    elif instance.text_type.name == 'translation':
        relation_name = 'translator'
    elif instance.text_type.name == 'review':
        relation_name = 'reviewer'
    for relation in instance.persontextrelation_set.all():
        if relation.relation_name == relation_name: persons.append(relation.person)
    names = [x.name for x in persons]
    urls = [instance_to_detail_url(x) for x in persons]
    return names, urls

def instance_to_detail_url(instance):
    return '/' + instance.detail_url.replace(':','/') + '/' + str(instance.pk) 


def instance_to_info_dict(instance):
    d = {}
    d['title'] = instance.title
    d['author_names'], d['author_urls'] = _get_author_name(instance)
    if instance.genre:
        d['genre'] = instance.genre.name
    else: d['genre'] = ''
    if instance.text_type:
        d['text_type'] = instance.text_type.name
    else: d['text_type'] = ''
    publications = instance.publications
    d['publication_titles'] = [p.title for p in publications]
    d['publication_years'] =[p.date.year for p in publications] 
    d['publication_years_str'] =', '.join(map(str,d['publication_years']))
    d['publication_pks'] = [p.pk for p in publications] 
    d['publication_urls'] = [instance_to_detail_url(p) for p in publications]
    d['detail_url'] = instance_to_detail_url(instance)
    d['setting'] = instance.setting
    d['language'] = instance.language_name
    d['serialized'] = serialize_instance(instance)
    return d

def flatten_list_of_list(list_of_list):
    output = []
    for l in list_of_list:
        output.extend(l)
    return output
    
    
def serialize_instance(instance):
    if not instance: return None
    f = serializers.serialize('json',[instance])
    return json.loads(f)[0]
    
    
