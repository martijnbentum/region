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
        d['original'] = instance_to_dict(original)
        if 'translation' in td.keys():
            d['translations'] = [instance_to_dict(x) for x in td['translation']]
        else: d['translations'] = []
        if 'review' in td.keys():
            d['reviews'] = [instance_to_dict(x) for x in td['review']]
        else: d['reviews'] = []
        d['titles'] = list(set([x.title for x in self.all_texts]))
        d['languages'] = self.languages
        d['original_title'] = original.title if original else ''
        d['original_language'] = original.language_name if original else ''
        d['original_author'] = original.language_name if original else ''
        self.d = d
        return d


def flatten_list_of_list(list_of_list):
    output = []
    for l in list_of_list:
        output.extend(l)
    return output
    
    
def instance_to_dict(instance):
    if not instance: return None
    f = serializers.serialize('json',[instance])
    return json.loads(f)
    
    
