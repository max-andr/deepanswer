import json
import requests
import pprint
import pandas as pd
from io import StringIO

pd.set_option('display.large_repr', 'truncate')
pd.set_option('display.max_columns', 0)
pd.set_option('max_colwidth', 25)

# import pymorphy2 as morph
# analyzer = morph.MorphAnalyzer()


def query_sparql(query, format_='csv'):
    url = 'http://dbpedia.org/sparql'
    params = {
        'query':             query,
        'default-graph-uri': 'http://dbpedia.org',
        'format':            format_,
        'sensor':            'false'
    }
    if format_ == 'csv':
        data = requests.get(url=url, params=params).text
    elif format_ == 'json':
        data = json.loads(requests.get(url=url, params=params).text)
    else:
        raise ValueError('Format is wrong')
    # pprint.pprint(data)
    return data


query = """
PREFIX owl: <http://dbpedia.org/ontology/>
PREFIX dbpprop: <http://dbpedia.org/property/>
SELECT distinct *
WHERE {
    ?person a owl:Person .
    ?person rdfs:label ?name .
    FILTER(lang(?name) = "ru")
}
LIMIT 10
"""
csv_response = query_sparql(query, format_='csv')
df = pd.read_csv(StringIO(csv_response))
# TODO: git propal, aaaa

print(df)



# TODO: natural_language -> parsed format -> SPARQL