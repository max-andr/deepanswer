import json
import requests


def lookup_keyword(string, cls, type_, max_hits=1):
    url = 'http://lookup.dbpedia.org/api/search/' + type_ + 'Search'
    params = {'QueryString': string,
              'QueryClass': cls,
              'MaxHits': max_hits}
    headers = {'Accept': 'application/json'}
    resp = json.loads(requests.get(url=url, params=params, headers=headers).text)
    if resp['results']:
        name = resp['results'][0]['label']
        description = resp['results'][0]['description']
        return name, description
    else:
        raise Exception('No results for <{0}> as <{1}Search>'.format(string, type_))


def print_autocomplete(string, cls):
    for i in range(1, len(string) + 1):
        prefix = string[:i]
        print(prefix, lookup_keyword(prefix, cls, 'Prefix'))


string, cls, type_ = 'Dnipropetrovsk', 'place', 'Prefix'
lookup_keyword(string, cls, type_)
# for key in resp['results'][0].keys():
#     print(key)
#     print(resp['results'][0][key])

print_autocomplete('Dnipropetrovsk', '')
print_autocomplete('Киев', '')

# TODO: translate api?



