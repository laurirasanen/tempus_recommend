from math import sqrt


def cosine_similarity(vec1, vec2):
    """ Manual function to calculate similarities between vectors.  """
    return sum(vec1 * vec2) / (sqrt(sum(vec1 ** 2)) * sqrt(sum(vec2 ** 2)))


def reduce_dict(inputdict):
    result = {}
    mapdict = {}
    mapdict_reverse = {}
    for key, value in inputdict.items():
        # 1 indexed
        new_entry = len(result) + 1
        result[new_entry] = value
        mapdict[key] = new_entry
        mapdict_reverse[new_entry] = key
    return result, mapdict, mapdict_reverse


def reduce_set(inputset):
    mapdict = {}
    mapdict_reverse = {}
    for value in inputset:
        # 1 indexed
        new_entry = len(mapdict) + 1
        mapdict[value] = new_entry
        mapdict_reverse[new_entry] = value
    return mapdict, mapdict_reverse
