from django.apps import apps
import glob
import os
import string
import json

def make_publication_identifier_to_texttype_dict(save = True):
    Publication= apps.get_model('catalogue','Publication')
    p = Publication.objects.all()
    d = {}
    for x in p:
        if not x.text_types: continue
        text_types = x.text_types
        if len(text_types) > 1 and 'original' in text_types:
            text_types.pop(text_types.index('original'))
        d[x.identifier] = text_types
    if save: save_json(d)
    return d

def save_json(d, filename = 'data/publication_texttype_dict.json'):
    with open(filename,'w') as fout:
        json.dump(d,fout)


def load_json(filename = 'data/publication_texttype_dict.json'):
    with open(filename,'r') as fin:
        d = json.load(fin)
    return d
        
