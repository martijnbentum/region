from django.urls import reverse
import json
from utils import search_view_helper as svh
from utils import model_util as mu
from utils import view_util as vu
import os
from pathlib import Path

exclude_names = []

def texts_linked_to_publication(publication):
    output = []
    for text in publication.texts:
        d = secondary_instance_to_json(text['text'])
        d['start_page'] = text['start_page']
        d['end_page'] = text['end_page']
        output.append(d)
    output = {'part_of_publication':output}
    output['reviewed_by']=secondary_instances_to_json(publication.reviews)
    return output

def illustration_linked_to_publication(text):
    output = []
    for illustration in text.illustrations:
        d = secondary_instance_to_json(illustration['illustration'])
        d['page'] = illustration['page']
        output.append(d)
    return {'part_of_publication':output}

def publication_to_json(publication, directory = 'rdr_rdr/'):
    d = secondary_instance_to_json(publication)
    d['form'] = publication.form.name if publication.form else None
    d['genres'] = publication.genres
    d['languages'] = publication.languages
    cr = publication.copyright
    d['copyright'] = cr.name if cr else None
    up = publication.use_permission
    d['use_permission'] = up.name if up else None
    if d['use_permission'] == 'no' or not up: 
        d['pdf_filename'] = None
        d['cover_filename'] = None
    else: 
        d['pdf_filename'] = publication.pdf.url if publication.pdf else None
        d['cover_filename']=publication.cover.url if publication.cover else None
    l = publication.location.all()
    d['locations'] = {'published_in':secondary_instances_to_json(l)}
    p = publication.publisher.all()
    d['publishers'] = {'published_by':secondary_instances_to_json(p)}
    d['persons'] = handle_general_relation_dict(publication.role_to_person_dict)
    d['texts'] = texts_linked_to_publication(publication)
    d['illustrations'] = illustration_linked_to_publication(publication)
    if d['use_permission'] == 'yes':
        if d['pdf_filename']:
            f = d['pdf_filename'].strip('/')
            os.system(f'cp {f} {directory}publication/pdf/')
        if d['cover_filename']:
            f = d['cover_filename'].strip('/')
            os.system(f'cp {f} {directory}publication/cover/')
    return d


def illustration_to_json(illustration, directory = 'rdr_rdr/'):
    d = secondary_instance_to_json(illustration)
    d['source_link'] = illustration.source_link
    d['description'] = illustration.description
    cr = illustration.copyright
    d['copyright'] = cr.name if cr else None
    up = illustration.use_permission
    d['use_permission'] = up.name if up else None
    if d['use_permission'] == 'no' or not up: d['filename'] = None
    else:d['filename']=illustration.upload.url if illustration.upload else None
    c = illustration.categories.all()
    d['categories'] = [x.name for x in c] if c else None
    t = illustration.illustration_type
    d['type'] = t.name if t else None
    d['persons'] = handle_general_relation_dict(illustration.roles_to_persons_dict)
    p = illustration.publications
    pn = illustration.page_number
    d['page_number'] = pn if pn else None
    d['publications'] = {'published_in':secondary_instances_to_json(p)}
    if d['use_permission'] == 'yes':
        if d['filename']:
            f = d['filename'].strip('/')
            os.system(f'cp {f} {directory}illustration/')
    return d

def movement_to_json(movement):
    d = secondary_instance_to_json(movement)
    d['type'] = movement.movement_type.name if movement.movement_type else None
    d['founded'] = movement.founded
    d['closure'] = movement.closure
    d['persons'] = handle_general_relation_dict(movement.role_to_person_dict)
    l = movement.location
    if not l: d['locations'] = None
    else: d['locations'] = {'located_in':secondary_instance_to_json(l)}
    return d

def periodical_to_json(periodical):
    d = secondary_instance_to_json(periodical)
    d['founded'] = periodical.founded
    d['closure'] = periodical.closure
    d['persons'] = handle_general_relation_dict(periodical.roles_to_persons_dict)
    p = periodical.publications
    d['publications'] = {'published':secondary_instances_to_json(p)}
    l = periodical.location.all()
    d['locations'] = {'located_in':secondary_instances_to_json(l)}
    return d

def publisher_to_json(publisher):
    d = secondary_instance_to_json(publisher)
    d['founded'] = publisher.founded
    d['closure'] = publisher.closure
    l = publisher.location.all()
    d['persons'] = {'managers': secondary_instances_to_json(publisher.persons)}
    p = publisher.publications
    d['publications'] = {'published':secondary_instances_to_json(p)}
    d['locations'] = {'located_in':secondary_instances_to_json(l)}
    return d

def location_to_json(location):
    d = secondary_instance_to_json(location)
    d['type'] = location.location_type.name if location.location_type else None
    d['region'] = location.region
    d['country'] = location.country
    d['latlng'] = location.latlng
    return d

def handle_general_relation_dict(relations_dict):
    if not relations_dict: return None
    d = {}
    for key, values in relations_dict.items():
        d[key] = secondary_instances_to_json(values)
    return d

def _handle_linked_locations(person):
    if not person.type_to_locations_dict: return None
    d = {}
    for location_type, locations in person.type_to_locations_dict.items():
        d[location_type] = [x for x in locations]
    return d

def person_to_json(person):
    d = secondary_instance_to_json(person)
    d['first_name'] = person.first_name
    d['last_name'] = person.last_name
    d['pseudonyms'] = person.pseudonyms.split(' | ')
    d['description'] = person.description
    d['gender'] = person.gender
    d['birth_year'] = person.birth_year
    d['death_year'] = person.death_year
    d['birth_place'] = person.birth_place.full_name if person.birth_place else None
    d['death_place'] = person.death_place.full_name if person.death_place else None
    d['vocations'] = person.vocations.split(', ')
    d['texts'] = handle_general_relation_dict(person.role_to_text_dict)
    ild = person.role_to_illustration_dict
    d['illustrations'] = handle_general_relation_dict(ild)
    pd = person.role_to_publication_dict
    d['publications'] = handle_general_relation_dict(pd)
    d['publishers'] = handle_general_relation_dict(person.role_to_publisher_dict)
    d['movements'] = handle_general_relation_dict(person.role_to_movement_dict)
    d['periodicals'] = handle_general_relation_dict(person.role_to_periodical_dict)
    d['persons'] = handle_general_relation_dict(person.role_to_person_dict)
    ld = person.type_to_location_intances_dict
    d['locations'] = handle_general_relation_dict(ld)
    bp, dp = person.birth_place, person.death_place
    bp = secondary_instance_to_json(bp) if bp else None
    dp = secondary_instance_to_json(person.death_place) if dp else None
    if not d['locations']: d['locations'] = {}
    d['locations']['birth_place'] = bp
    d['locations']['death_place']= dp
    return d

def _handle_linked_texts(text):
    if not text.type_to_linked_texts_dict: return None
    d = {}
    for text_type, texts in text.type_to_linked_texts_dict.items():
        if text.type_info == text_type == 'translation': k = 'translation_of'
        elif text_type == 'translation': k = 'translations'
        else: k = text_type
        d[k] = []
        for t in texts:
            temp = secondary_instance_to_json(t)
            temp['language'] = t.language.name
            d[k].append(temp)
    return d

def _handle_linked_persons(instance):
    if not instance.roles_to_persons_dict: return None
    d = {}
    for role, persons in instance.roles_to_persons_dict.items():
        d[role] = secondary_instances_to_json(persons) 
    return d

def _handle_reviews(text):
    if not text.reviews: return None
    review_type = text.reviews['type']
    items = text.reviews['reviews']
    d = {review_type:secondary_instances_to_json(items)}
    return d

def text_to_json(text):
    d = secondary_instance_to_json(text)
    d['description'] = text.description
    d['genre'] = text.genre.name if text.genre else None
    d['language'] = text.language.name if text.language else None
    d['setting_name'] = text.setting
    d['locations']={'setting':secondary_instances_to_json(text.location.all()) }
    d['texts'] = _handle_linked_texts(text)
    d['persons'] = _handle_linked_persons(text)
    d['publication_years'] = sorted(list(set(text.get_years)))
    d['publications'] = secondary_instances_to_json(text.publications)
    d['reviews'] = _handle_reviews(text)
    return d

def secondary_instances_to_json(instances):
    return [secondary_instance_to_json(x) for x in instances if x]

def secondary_instance_to_json(instance):
    d = {}
    if type(instance) == str:
        d['name'] = instance
        d['identifier'] = None
        d['model_name'] = None
        d['url'] = None
        return d
    model_name = instance._meta.model_name
    print(f'{model_name} {instance.pk} {instance}')
    d['name'] = str(instance)
    if model_name.lower() in exclude_names: 
        d['identifier'] = None
        d['url'] = None
    else:    
        d['identifier'] = instance.identifier
        d['url'] = get_url(instance)
    d['model_name'] = model_name
    return d

def contributer_list(instance):
    c = vu.Crud(instance)
    cl = c.contributer_list
    return [x for x in cl if x != '' and x != 'mb']
    

def get_image_filenames(instance, image_dir):
    urls = mu.instance2image_urls(instance)
    if type(urls) == str: urls = [urls]
    fn = [Path(x).name for x in urls]
    if fn == ['']: fn = []
    o = []
    for f in fn:
        path = Path(f'{image_dir}images/{f}')
        if not path.exists(): 
            print(f'File not found: {path}')
            continue
        print('adding file:', path)
        o.append(str(path).replace(image_dir, ''))
    return o

def get_url(instance, base_url = 'redefiningtheregion.rich.ru.nl'):
    if instance._meta.model_name in exclude_names: return ''
    if not hasattr(instance, 'detail_url'): return ''
    url = reverse(instance.detail_url, kwargs = {'pk': instance.pk})
    return f'{base_url}{url}'

def _instance_to_location_ids(instance):
    if not 'locations' in instance.keys(): return []
    if not instance['locations']: return []
    ids = []
    for k, v in instance['locations'].items():
        if type(v) == dict: 
            ids.append(v['identifier'])
        elif type(v) == list:
            for l in v:
                ids.append(l['identifier'])
        elif v == None: pass
        else: 
            print(instance, v)
            raise ValueError(f'Unknown type {type(v)}')
    return ids
        

def used_locations_to_json(d = None):
    from locations.models import Location
    if not d: d = make_all_detail_views()
    ids = []
    for k, instances in d.items():
        if 'locations' not in instances[0].keys(): 
            print(f'No locations in {k}')
            continue
        for instance in instances:
            temp = _instance_to_location_ids(instance)
            for identifier in temp:
                ids.append(identifier.split('_')[-1])
    ids = list(set(ids))
    output = []
    for id in ids:
        location = Location.objects.get(pk= id)
        output.append(location_to_json(location))
    return output
        

def make_all_detail_views(save = False, 
    output_dir = 'rdr_rdr/', name = 'main_data.json'):
    output = {}
    models = mu.get_all_models()
    for model in models:
        model_name = model._meta.model_name
        output[model_name] = []
        f = globals().get(f'{model_name}_to_json')
        print(f'Processing {model_name} {f}')
        instances = model.objects.all()
        for x in instances:
            print(f'Processing {model_name} {x.pk} {x}')
            d = f(x)
            output[model_name].append(d)
    output['location'] = used_locations_to_json(output)
    if save:
        filename = f'{output_dir}{name}'
        print(f'Saving to {filename}')
        with open(filename, 'w') as f:
            json.dump(output, f, indent = 4)
    return output
        

