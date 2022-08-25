from django.apps import apps
import glob
from . import model_util
from operator import attrgetter
import os
import string
import json

def make_all():
    make_instances_identifier_to_texttype_dict()
    make_instances_identifier_to_language_dict()
    make_instances_identifier_to_genre_dict()
    make_instances_identifier_to_gender_dict()
    make_instances_identifier_to_locationtype_dict()


def make_identifier_to_attribute_dict(model,attribute_name,filename = ''):
    instances = model.objects.all()
    d = {}
    f = attrgetter(attribute_name)
    for instance in instances:
        try: attribute = f(instance)
        except AttributeError: continue
        if attribute:
            d[instance.identifier] = attribute
    if filename: save_json(d,filename)
    return d
        
        
def make_instances_identifier_to_texttype_dict(save = True):
    Publication= apps.get_model('catalogue','Publication')
    Text= apps.get_model('catalogue','Text')
    d = make_identifier_to_attribute_dict(Publication,'text_types')
    d.update(make_identifier_to_attribute_dict(Text,'text_type.name'))
    if save:
        filename = 'data/instances_texttype_dict.json'
        save_json(d, filename)
    return d

def make_instances_identifier_to_language_dict(save = True):
    Publication= apps.get_model('catalogue','Publication')
    Text= apps.get_model('catalogue','Text')
    d = make_identifier_to_attribute_dict(Publication,'languages')
    d.update(make_identifier_to_attribute_dict(Text,'language.name'))
    if save:
        filename = 'data/instances_language_dict.json'
        save_json(d, filename)
    return d

def make_instances_identifier_to_genre_dict(save = True):
    Publication= apps.get_model('catalogue','Publication')
    Text= apps.get_model('catalogue','Text')
    d = make_identifier_to_attribute_dict(Publication,'genres')
    d.update(make_identifier_to_attribute_dict(Text,'genre.name'))
    if save:
        filename = 'data/instances_genre_dict.json'
        save_json(d, filename)
    return d

def make_instances_identifier_to_gender_dict(save = True):
    Publication= apps.get_model('catalogue','Publication')
    Text= apps.get_model('catalogue','Text')
    Illustration= apps.get_model('catalogue','Illustration')
    d = make_identifier_to_attribute_dict(Publication,'genders')
    d.update(make_identifier_to_attribute_dict(Text,'genders'))
    d.update(make_identifier_to_attribute_dict(Illustration,'genders'))
    if save:
        filename = 'data/instances_gender_dict.json'
        save_json(d, filename)
    return d

def make_instances_identifier_to_locationtype_dict(save = True):
    instances = model_util.get_all_instances()
    d = {}
    for instance in instances:
        if hasattr(instance,'setting_location_pks'):
            names = []
            if instance.setting_location_pks: names.append('setting')
            if instance.publication_location_pks: names.append('publication')
            if names: d[instance.identifier] = names
    if save:
        filename = 'data/instances_locationtype_dict.json'
        save_json(d, filename)
    return d
    

def load_json_texttype():
    filename = 'data/instances_texttype_dict.json'
    return load_json(filename)

def load_json_language():
    filename = 'data/instances_language_dict.json'
    return load_json(filename)

def load_json_genre():
    filename = 'data/instances_genre_dict.json'
    return load_json(filename)

def load_json_gender():
    filename = 'data/instances_gender_dict.json'
    return load_json(filename)

def load_json_locationtype():
    filename = 'data/instances_locationtype_dict.json'
    return load_json(filename)


def save_json(d, filename ):
    with open(filename,'w') as fout:
        json.dump(d,fout)


def load_json(filename):
    with open(filename,'r') as fin:
        d = json.load(fin)
    return d

