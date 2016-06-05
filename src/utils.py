from functools import reduce


def unique_values(seq) -> list:
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def argmax(values: list) -> int:
    return max(enumerate(values), key=lambda x: x[1])[0]

def multi_replace(string: str, replace_tuples: tuple) -> str:
    return reduce(lambda a, kv: a.replace(*kv), replace_tuples, string)