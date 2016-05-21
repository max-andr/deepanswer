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
LIMIT 10
"""

data = query_sparql(query)
pprint.pprint(data)
