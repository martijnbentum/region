from django.db import IntegrityError
from collections import Counter
import string
from utilities.models import Queryterm

punctuation = string.punctuation + '“”«»’'

STOPWORDS = frozenset({
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'also', 'am',
    'an', 'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'before',
    'being', 'below', 'between', 'both', 'but', 'by', 'can', 'could', 'dans',
    'de', 'der', 'des', 'die', 'dit', 'do', 'does', 'doing', 'don', 'down',
    'du', 'during', 'een', 'eens', 'en', 'er', 'es', 'est', 'et', 'few',
    'for', 'from', 'further', 'had', 'has', 'have', 'having', 'he', 'her',
    'here', 'hers', 'herself', 'het', 'him', 'himself', 'his', 'how', 'ich',
    'if', 'ik', 'il', 'ils', 'im', 'in', 'into', 'is', 'it', 'its', 'itself',
    'je', 'jij', 'jusqu', 'la', 'le', 'les', 'me', 'meer', 'met', 'mich',
    'mijn', 'moi', 'mon', 'most', 'my', 'myself', 'naar', 'nach', 'ne', 'niet',
    'no', 'nor', 'not', 'nous', 'of', 'off', 'om', 'on', 'once', 'ons',
    'onze', 'ook', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over',
    'own', 'pas', 'pour', 'same', 'sich', 'sie', 'so', 'some', 'son', 'such',
    'sur', 'te', 'than', 'that', 'the', 'their', 'theirs', 'them',
    'themselves', 'then', 'there', 'these', 'they', 'this', 'those', 'through',
    'to', 'too', 'under', 'und', 'une', 'up', 'van', 'very', 'via', 'von',
    'voor', 'was', 'wat', 'we', 'weer', 'werden', 'what', 'when', 'where',
    'which', 'while', 'wie', 'wij', 'will', 'with', 'worden', 'would', 'you',
    'your', 'yours', 'yourself', 'yourselves', 'ze', 'zelf', 'zich', 'zij',
    'zo', 'zu'
})

def handle_stop_words(words):
    output = []
    for word in words:
        w = word.lower()
        if w in STOPWORDS: continue
        output.append(word)
    return output

def check_start(word):
    remove_char = 0
    for word_character in word:
        if word_character not in punctuation: break
        else: remove_char += 1
    if remove_char == 0: return word
    if len(word) <= remove_char: return ''
    return word[remove_char:]

def check_end(word):
    remove_char = 0
    for word_character in word[::-1]:
        if word_character not in punctuation: break
        else: remove_char += 1
    if remove_char == 0: return word
    if len(word) <= remove_char: return ''
    return word[:-1*remove_char]


def handle_punctuation(words):
    output = []
    for word in words:
        word = check_start(word)
        word = check_end(word)
        if not word: continue
        if '.' in word: continue
        output.append(word)
    return output
    
def handle_word_length(words):
    output = []
    for word in words:
        if len(word) < 4: continue
        output.append(word)
    return output

def handle_comma_and_dash(words):
    output= []
    for word in words:
        if ',' in word: output.extend(word.split(','))
        elif '_' in word: output.extend(word.split('_'))
        elif '--' in word: output.extend(word.split('--'))
        else: output.append(word)
    return output

def handle_weird_words(words):
    output= []
    for word in words:
        if word.startswith('0'): continue
        output.append(word)
    return output


def text_to_unigrams(text):
    text = text.replace('\r\n',' ')
    text = text.replace('\n',' ')
    words = [word for word in text.split(' ') if word]
    words = handle_comma_and_dash(words)
    words = handle_weird_words(words)
    words = handle_punctuation(words)
    words = handle_word_length(words)
    words = handle_stop_words(words)
    words = [word.lower() for word in words]
    return Counter(words)

def update_queryterms(terms):
    already_present = 0
    added = 0
    for term in terms:
        t = Queryterm(term = term)
        try: t.save()
        except IntegrityError: 
            already_present += 1
            continue
        else: added += 1
    print('already_present:',already_present,'added:',added)
    
def get_queryterms():
    qh = Queryterm.objects.all()
    terms = [x.term for x in qh]
    return sorted(terms)

            
    
