import re
import json
import requests
import pprint
import pandas as pd
from io import StringIO

pd.set_option('display.large_repr', 'truncate')
# tables in 1 line
# pd.set_option('display.max_columns', 0)
# set width of 1 column
pd.set_option('max_colwidth', 35)

# import pymorphy2 as morph
# analyzer = morph.MorphAnalyzer()


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
    elif format_ == 'json':
        data = json.loads(requests.get(url=url, params=params).text)
    else:
        raise Exception('Response format is wrong.')
    # explicit error handling
    if re.findall("Virtuoso \d+ Error", data):
        raise Exception(data)
    # pprint.pprint(data)
    return data


query = """
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbprop: <http://dbpedia.org/property/>
SELECT distinct *
WHERE {
    dbprop:Гранд_Макет_Россия
    ?dbpedia_url rdf:type dbo:Place .
    ?dbpedia_url rdfs:label ?name .
    FILTER(lang(?name) = 'ru')
}
LIMIT 20
"""
csv_response = query_sparql(query, format_='csv')
df = pd.read_csv(StringIO(csv_response))

print(df)


# TODO: natural_language -> syntax parsed format -> SPARQL
# TODO: Named Entity Recognition! Find out, what word is central?
# TODO: type of question as multi-class text categorization.
# But history on russian Qs?
# probably some heuristics will work.

# intermediate format example
# "person": "Tim Berners-Lee"
# "birth place": "London, UK"

# TODO: question type classification