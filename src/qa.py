import re
import json
import requests
import pymorphy2
import pprint
import pandas as pd
from io import StringIO
from sklearn.feature_extraction.text import CountVectorizer

pd.set_option('display.large_repr', 'truncate')
# tables in 1 line
# pd.set_option('display.max_columns', 0)
# set width of 1 column
pd.set_option('max_colwidth', 35)


def query_sparql(query, format_='csv'):
    url = 'http://dbpedia.org/sparql'
    params = {
        'query':             query,
        'default-graph-uri': 'http://dbpedia.org',
        'format':            format_,
        'sensor':            'false',
        'timeout':           30000
    }
    if format_ == 'csv':
        data = requests.get(url=url, params=params).text
    elif format_ in ('json',):
        string = requests.get(url=url, params=params).text
        data = json.loads(string)
    else:
        raise Exception('Response format is wrong.')
    # explicit error handling
    if re.findall("Virtuoso \d+ Error", str(data)):
        raise Exception(data)
    # pprint.pprint(data)
    return data


def get_property_descr(prop_url):
    rdfs_descr = {'label':   'http://www.w3.org/2000/01/rdf-schema#label',
                  'comment': 'http://www.w3.org/2000/01/rdf-schema#comment'}
    r_json = query_sparql('DESCRIBE <{0}>'.format(prop_url), format_='json')
    descr = ''
    for spo in r_json['results']['bindings']:
        # if the given predicate is description (label or comment for ontology/property)
        if spo['p']['value'] in rdfs_descr.values():
            descr += spo['o']['value'] + '\n'
    return descr


query = """
select distinct ?property, ?subject, ?obj
where {{
     ?subject a <{0}> .
     ?subject ?property ?obj .
     FILTER(?subject=<{1}>)
}}
limit 200000
"""
# values ?target {dbpedia:Dnepr}

csv_response = query_sparql(query, format_='csv')
df = pd.read_csv(StringIO(csv_response))
print(df)



# http://dbpedia.org/property/timezone
uri = lookup_keyword('Dnipropetrovsk')[0]
# TODO: определять Place or Settlement or ... через Lookup

query_with_values = query.format('http://dbpedia.org/ontology/Place', uri)
r_json = query_sparql(query_with_values, format_='json')
pprint.pprint(r_json)
# TODO: по каждому property получить описание функцией get_property_descr
подлежащее - тоже класс с разными методами
property/ontology сделать как класс с методом получения описания
sparql и лукап запросы в модуль dbpedia_api

prop_descr = get_property_descr('http://dbpedia.org/property/julPrecipitationMm')
print(prop_descr)

# TODO: natural_language -> syntax parsed format -> SPARQL
# TODO: Named Entity Recognition! Find out, what word is central?
# TODO: type of question as multi-class text categorization.
# But history on russian Qs?
# probably some heuristics will work.

# intermediate format example
# "person": "Tim Berners-Lee"
# "birth place": "London, UK"

# TODO: question type classification

question = 'В какой стране родился Линкольн?'
birthPlace = ?, entity = Lincoln

1. найти сказуемое (глагол)
2. edit distance: birth -> birthPlace
# question = 'В какой стране живёт Линкольн?'
# question = 'В какой стране находится Днепропетровск?'
q_constructions = {'в каком году':   ['year'],
                   'в каком городе': ['place'],
                   'в какой стране': ['country'],
                   'где находится':  ['place', 'country'],
                   '':               ''}
q_verb = {'родиться':   ['birthPlace'],
          'находиться': ['situatedIn'],
          'жить':       ['livesIn']}

morph = pymorphy2.MorphAnalyzer()
vect = CountVectorizer(ngram_range=(1, 3))
vect.fit_transform([question])

# TODO: токенайзер придумать (на почте)
ngrams = vect.get_feature_names()
print(ngrams)

for ngram in [ngram for ngram in ngrams if len(ngram.split()) == 1]:
    pos = morph.parse(ngram)[0].tag.POS
    print(ngram, '__', pos)

# TODO: 2 большие буквы
# TODO: multi-class classification по каждому вопросу;
# предсказать relationType (bornIn, livesIn, aKindOf);
# обучаться на Википедии; ... born in ... - предложение with positive label.

