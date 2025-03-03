from django.urls import reverse
import json
from utils import search_view_helper as svh
from utils import model_util as mu
from utils import view_util as vu
from pathlib import Path

exclude_names = []

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
    d['description'] = person.description
    d['gender'] = person.gender
    d['birth_year'] = person.birth_year
    d['death_year'] = person.death_year
    d['birth_place'] = person.birth_place.name if person.birth_place else None
    d['death_place'] = person.death_place.name if person.death_place else None
    d['vocations'] = person.vocations
    d['linked_locations'] = _handle_linked_locations(person)
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
    d['setting'] = text.setting
    d['linked_texts'] = _handle_linked_texts(text)
    d['linked_persons'] = _handle_linked_persons(text)
    d['publication_years'] = sorted(list(set(text.get_years)))
    d['publications'] = secondary_instances_to_json(text.publications)
    d['reviews'] = _handle_reviews(text)
    return d

def secondary_instances_to_json(instances):
    return [secondary_instance_to_json(x) for x in instances]

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
    url = reverse(instance.detail_url, kwargs = {'pk': instance.pk})
    return f'{base_url}{url}'
    

def instance_to_json(instance, 
    image_dir = 'rdr_hoh/'):
    d = secondary_instance_to_json(instance)
    fields = ['title_original', 'title_english', 'date_field', 'description']
    fields += ['source_link', f'{instance._meta.model_name}_type']
    for field in fields:
        if hasattr(instance, field): 
            value = getattr(instance, field)
            if 'type' in field: field = 'type'
            if field in ['date_field', 'type']: 
                value = str(value)
            d[field] = value
        else: 
            if 'type' in field: field = 'type'
            d[field] = None
    image_filenames = get_image_filenames(instance, image_dir)
    d['image_filenames'] = image_filenames
    d['keywords'] = instance.keyword_names.split(', ')
    if instance._meta.model_name == 'person':
        d['viaf'] = instance.viaf
        d['pseudonyms'] = instance.pseudonyms
    d['meta_data_contributer_list'] = contributer_list(instance)
    return d

def args_to_json(args, instance = None):
    if not instance: instance = args['instance']
    d = {'instance': instance_to_json(instance), 'connections': {}}
    for key, value in args.items():
        if key in ['us','instance','page_name']: continue
        f = secondary_instance_to_json
        d['connections'][key] = [f(instance) for instance in value]
    return d

def make_all_detail_views(save = False, 
    output_dir = 'rdr_hoh/', name = 'main_data.json'):
    instances = mu.get_all_instances(flag_filter_person = False,
        add_famine = True)
    output = {}
    for x in instances:
        model_name = x._meta.model_name
        print(f'Processing {model_name} {x.pk} {x}')
        if model_name not in output.keys(): output[model_name] = []
        args = detail_args(x)
        d = args_to_json(args, x)
        output[model_name].append(d)
    if save:
        filename = f'{output_dir}{name}'
        print(f'Saving to {filename}')
        with open(filename, 'w') as f:
            json.dump(output, f, indent = 4)
    return output
        

