from functools import reduce
from urllib.parse import urlparse
import time


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print('Time: %2.2f sec, function: %r, args: (%r, %r).' % (te - ts, method.__name__, args, kw))
        return result

    return timed


def is_link(string):
    p = urlparse(string)
    if p.scheme in ('http', 'https') and p.netloc != '' and p.path != '':
        return True
    else:
        return False


def is_dbpedia_link(prop):
    return 'http://dbpedia.org/' in prop


def extract_link_entity(string):
    p = urlparse(string)
    if p.scheme in ('http', 'https') and p.netloc != '' and p.path != '':
        last_val_after_slash = p.path.split('/')[-1]
        return last_val_after_slash.replace('_', ' ')


def unique_values(seq) -> list:
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def argmax(values: list) -> int:
    return max(enumerate(values), key=lambda x: x[1])[0]


def multi_replace(string: str, replace_tuples: tuple) -> str:
    return reduce(lambda a, kv: a.replace(*kv), replace_tuples, string)
