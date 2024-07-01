import Levenshtein
import re

def load_locations():
    from locations.models import Location
    locations = Location.objects.all()
    return locations

def select_manually_added_locations(locations = None):
    if not locations: locations = load_locations()
    output = [x for x in locations if not re.match(r'^\d+$', x.geonameid)]
    return output

def check_location_matches(manually_added_locations = None, locations = None,
    max_distance = 2):
    if not locations: locations = load_locations()
    if not manually_added_locations: 
        manually_added_locations = select_manually_added_locations(locations)
    output = {}
    for location in manually_added_locations:
        name = location.name
        pk = location.pk
        for l in locations:
            if l.pk == pk: continue
            if check_match(name, l.name, max_distance):
                if not pk in output.keys(): output[pk] = []
                output[pk].append(l.pk)
    return output

def check_match(str1,str2, min_distance = 0, max_distance = 2):
    distance = Levenshtein.distance(str1, str2)
    match = min_distance <= distance <= max_distance
    return match


def load_texts():
    from catalogue.models import Text
    texts = Text.objects.all()
    return texts

def check_text_matches(texts = None, min_distance = 1, max_distance = 2):
    if not texts: texts = load_texts()
    output = {}
    for text1 in texts:
        setting = text1.setting
        if not setting: continue
        pk = text1.pk
        for text2 in texts:
            if text2.pk == pk: continue
            if not setting: continue
            if text2.pk in output.keys(): 
                if pk in output[text2.pk]: continue
            if check_match(setting, text2.setting, min_distance, max_distance):
                if not pk in output.keys(): output[pk] = []
                output[pk].append(text2.pk)
    return output
