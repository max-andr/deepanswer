import re
import json
from collections import defaultdict

import nltk
import requests
import pymorphy2
import pprint
import pandas as pd
from io import StringIO

from SPARQLWrapper import SPARQLWrapper, JSON
from microsofttranslator import Translator
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

pd.set_option('display.large_repr', 'truncate')
# tables in 1 line
# pd.set_option('display.max_columns', 0)
# set width of 1 column
pd.set_option('max_colwidth', 35)


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


def query_sparql(query):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)
    return sparql.query().convert()


class Property:
    # TODO: test if it works
    cached_prop_descr = dict()

    def __init__(self, uri):
        self.uri = uri

    def get_descr(self):
        if self.uri in self.cached_prop_descr:
            descr = self.cached_prop_descr[self.uri]
        else:
            rdfs_descr = {'label':   'http://www.w3.org/2000/01/rdf-schema#label',
                          'comment': 'http://www.w3.org/2000/01/rdf-schema#comment'}
            r_json = query_sparql('DESCRIBE <{0}>'.format(self.uri))
            descr = ''
            for spo in r_json['results']['bindings']:
                # if the given predicate is description (label or comment for ontology/property)
                if spo['p']['value'] in rdfs_descr.values():
                    descr += spo['o']['value'] + '\n'
            self.cached_prop_descr[self.uri] = descr
        return descr


class Entity:
    def __init__(self, uri):
        self.uri = uri
        self.properties =

    def get_properties(self):
        """
        :param uri: URI of some entity
        :return: dictionary {property: value} for the entity
        """
        query = """
        select distinct ?property, ?subject, ?obj
        where {{
             ?subject a <{0}> .
             ?subject ?property ?obj .
             FILTER(?subject=<{1}>)
        }}
        """
        query_with_values = query.format('http://dbpedia.org/ontology/Place', self.uri)
        r_json = query_sparql(query_with_values)
        prop_dict = defaultdict(list)
        for spo in r_json['results']['bindings']:
            prop_uri = spo['property']['value']
            prop_value = spo['obj']['value']
            prop_dict[prop_uri] += [prop_value]
        return prop_dict


question = translate('Какой почтовый код у Днепропетровска?')
q_words = nltk.word_tokenize(question)
# TODO: логика выделения существительного

main_word = 'Dnipropetrovsk'
entity_uri = lookup_keyword(main_word)[0]
# TODO: определять Place or Settlement or ... через Lookup

entity = Entity(entity_uri)
prop_dict = entity.get_properties()

prop_descr_dict = dict()
for key in prop_dict.keys():
    prop_descr_dict[key] = Property(key).get_descr()
    print("Fetching property descriptions:", prop_descr_dict[key])


# TODO: в функцию обернуть тоже
# restrict vocabulary only to words in questions
vect = CountVectorizer(ngram_range=(1, 3),
                       vocabulary=filter(lambda w: w != main_word, q_words))
# TODO: change to TF-IDF vectorizer
props_matrix = vect.fit_transform(prop_descr_dict.values())
q_vector = vect.transform([question])

sims = cosine_similarity(q_vector, props_matrix).flatten()
top_sims = sims.argsort()[:-5:-1]
print(top_sims)
как бы получить по номеру ссылку на сущность?
# TODO: токенайзер придумать (на почте)
ngrams = vect.get_feature_names()
print(ngrams)

# TODO: по каждому property получить описание функцией get_property_descr
# подлежащее - тоже класс с разными методами
# property/ontology сделать как класс с методом получения описания
# sparql и лукап запросы в модуль dbpedia_api

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

# question = 'В какой стране родился Линкольн?'
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

