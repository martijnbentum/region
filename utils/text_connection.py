from django.core import serializers
import json

class text_connection:
    def __init__(self,text):
        self.start_text = text
        self.type = text.type_info
        self.is_translation = self.type == 'translation'
        self.is_review = self.type == 'review'
        self.get_original()
        self.collect_translations()

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
    name = ', '.join([x.name for x in persons])
    return name


def instance_to_info_dict(instance):
    d = {}
    d['title'] = instance.title
    d['author'] = _get_author_name(instance)
    if instance.genre:
        d['genre'] = instance.genre.name
    else: d['genre'] = ''
    if instance.text_type:
        d['text_type'] = instance.text_type.name
    else: d['text_type'] = ''
    d['publication_titles'] = [p.title for p in instance.publications]
    d['publication_years'] =[p.date.year for p in instance.publications] 
    d['publication_years_str'] =', '.join(map(str,d['publication_years']))
    d['publication_pks'] = [p.pk for p in instance.publications] 
    d['publication_detail_url'] = 'catalogue:detail_publication'
    d['detail_url'] = instance.detail_url
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
    
    
