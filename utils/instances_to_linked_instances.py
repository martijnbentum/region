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
    if save: 
        filename = 'data/publication_texttype_dict.json'
        save_json(d, filename)
    return d

def make_publication_identifier_to_languages_dict(save = True):
    Publication= apps.get_model('catalogue','Publication')
    p = Publication.objects.all()
    d = {}
    for x in p:
        if not x.languages: continue
        languages= x.languages
        d[x.identifier] = languages 
    if save: 
        filename = 'data/publication_language_dict.json'
        save_json(d, filename)
    return d

def make_publication_identifier_to_genre_dict(save = True):
    Publication= apps.get_model('catalogue','Publication')
    p = Publication.objects.all()
    d = {}
    for x in p:
        if not x.genres : continue
        genres= x.genres
        d[x.identifier] = genres
    if save: 
        filename = 'data/publication_genre_dict.json'
        save_json(d, filename)
    return d

def make_text_identifier_to_texttype_dict(save = True):
    Text= apps.get_model('catalogue','Text')
    t = Text.objects.all()
    d = {}
    for x in t:
        if not x.text_type: continue
        language= x.text_type.name
        d[x.identifier] = language 
    if save: 
        filename = 'data/text_texttype_dict.json'
        save_json(d, filename)
    return d

def make_text_identifier_to_languages_dict(save = True):
    Text= apps.get_model('catalogue','Text')
    t = Text.objects.all()
    d = {}
    for x in t:
        if not x.language: continue
        language= x.language.name
        d[x.identifier] = language 
    if save: 
        filename = 'data/text_language_dict.json'
        save_json(d, filename)
    return d

def make_text_identifier_to_genre_dict(save=True):
    Text= apps.get_model('catalogue','Text')
    t = Text.objects.all()
    d = {}
    for x in t:
        if not x.genre: continue
        genre= x.genre.name
        d[x.identifier] = genre 
    if save: 
        filename = 'data/text_genre_dict.json'
        save_json(d, filename)
    return d


def save_json(d, filename ):
    with open(filename,'w') as fout:
        json.dump(d,fout)


def load_json(filename):
    with open(filename,'r') as fin:
        d = json.load(fin)
    return d

def load_json_publication_texttypes():
    filename = 'data/publication_texttype_dict.json'
    return load_json(filename)

def load_json_publication_languages():
    filename = 'data/publication_language_dict.json'
    return load_json(filename)

def load_json_publication_genre():
    filename = 'data/publication_genre_dict.json'
    return load_json(filename)

def load_json_text_languages():
    filename = 'data/text_language_dict.json'
    return load_json(filename)

def load_json_text_texttypes():
    filename = 'data/text_texttype_dict.json'
    return load_json(filename)

def load_json_text_genre():
    filename = 'data/text_genre_dict.json'
    return load_json(filename)
        
