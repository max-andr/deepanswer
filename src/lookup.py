import json
import requests
import nltk
from microsofttranslator import Translator


def translate(string, to_lang='en'):
    translator = Translator('max-andr', '36OSL0SDYEtJCS1Z9kmDvbXkaOFeriDcB2ZvLSAA+q8=')
    return translator.translate(string, to_lang)


def lookup_keyword(string, cls='', type_='Keyword', max_hits=1):
    url = 'http://lookup.dbpedia.org/api/search/' + type_ + 'Search'
    params = {'QueryString': string,
              'QueryClass':  cls,
              'MaxHits':     max_hits}
    headers = {'Accept': 'application/json'}
    resp = json.loads(requests.
                      get(url=url, params=params, headers=headers).
                      text)
    if resp['results']:
        res = resp['results'][0]
        uri = res['uri']
        name = res['label']
        description = res['description']
        classes = [cls['uri'] for cls in res['classes']]
        return uri, name, description, classes
    else:
        print('No results for <{0}> of class <{1}> (<{2}Search>)'.
              format(string, cls, type_))


def print_autocomplete(string, cls):
    for i in range(1, len(string) + 1):
        prefix = string[:i]
        print(prefix, lookup_keyword(prefix, cls, 'Prefix'))


string, cls, type_ = 'Dnipropetrovsk', 'place', 'Prefix'
lookup_keyword(string, cls, type_)
lookup_keyword('Dnipropetrovsk')
lookup_keyword('Abraham Lincoln')
Agent -> Person -> OfficeHolder
get all relations for given CLASS (to restrict possible reasoning)

использовать ontology:comment при матчинге вопроса и свойства (TF-IDF)
ссылки на онтологию (описания entity) разные. использовать только DBPedia?

ontology описывает entity: Class, ObjectProperty, ...
rdfs:domain - область допустимых свойств
rdfs:range - область допустимых значений
подготовить это всё в виде теоретической части

lookup_keyword('Авраам Линкольн')

question = 'В какой стране родился Линкольн?'
question = 'Чем знаменит Линкольн?'
question = 'Кто был убит в Вашингтоне?'


# for key in resp['results'][0].keys():
#     print(key)
#     print(resp['results'][0][key])

print_autocomplete('Dnipropetrovsk', '')
print_autocomplete('Киев', '')

question = translate('Где находится Днепропетровск?')
print(question)


for token in nltk.word_tokenize(question):
    # only NOUNs
    found = lookup_keyword(token)
    print(token, '\n', found, '\n')

