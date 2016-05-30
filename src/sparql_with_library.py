import json
import pprint
import requests
from SPARQLWrapper import SPARQLWrapper, JSON


def query_sparql(query):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)

    sparql.setQuery(query)

    return sparql.query().convert()

query = """
PREFIX dbres: <http://dbpedia.org/resource/>
DESCRIBE dbres:Dnipro
LIMIT 10d
"""

data = query_sparql(query)
pprint.pprint(data)





"""
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
"""