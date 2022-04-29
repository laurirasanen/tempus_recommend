from __future__ import division
import numpy as np

np.random.seed(13)

import keras.backend as K
from keras.models import Sequential
from keras.layers import Dense, Embedding, Reshape, Lambda, Subtract
from keras.utils import np_utils
from keras.utils.data_utils import get_file
from keras.preprocessing.text import Tokenizer
from keras.utils.vis_utils import model_to_dot
from keras.preprocessing import sequence

from .db import get_tts
from .util import reduce_set, reduce_dict, cosine_similarity

nfeatures = 600
num_times = 50
player_class = 0
modelname = ""
FEATURE_MODEL = None
M = None
P = None
playermap = None
playermap_reverse = None
mapdata_reduced = None
mapdata_reduced_map = None
mapdata_reduced_map_reversed = None
map_to_id = None
id_to_map = None


def _init_model(features, maps, players):
    model = Sequential()
    model.add(Embedding(input_dim=maps, output_dim=features, input_length=1))
    model.add(Reshape((features,)))
    model.add(Dense(input_dim=features, units=players, activation="softmax"))
    model.compile(
        loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"]
    )
    return model


def _get_feature_vector(model):
    vectors = model.get_weights()[0]
    features = vectors.shape[1]
    top = vectors.shape[0]
    feature_vector = np.zeros((vectors.shape[0], features))

    for i in range(0, top):
        for j in range(0, features):
            feature_vector[i][j] = vectors[i][j]
    return feature_vector


def _gen_training():
    global M
    global P
    global playermap
    global playermap_reverse
    global mapdata_reduced
    global mapdata_reduced_map
    global mapdata_reduced_map_reversed
    global map_to_id
    global id_to_map

    # generate training data for neural net
    playerset, tts, map_to_id, id_to_map = get_tts(num_times, player_class)
    playermap, playermap_reverse = reduce_set(playerset)
    mapdata_reduced, mapdata_reduced_map, mapdata_reduced_map_reversed = reduce_dict(
        tts
    )

    # 1 indexed
    P = len(playermap) + 1
    M = len(mapdata_reduced) + 1


def _get_dimensions():
    x = []
    y = []

    for mapid, ttlist in mapdata_reduced.items():
        for i, time in enumerate(ttlist):
            # not enough times, skip this data
            if time == 0:
                continue
            # append reverse of tt height, i.e. rank 0 gets appended 10 times etc
            for j in range(0, num_times - i):
                x.append(mapid)
                y_onehot = np.zeros(P)
                y_onehot[playermap[time]] = 1
                y.append(y_onehot)

    # to np array
    x = np.asarray(x)
    y = np.asarray(y)
    return x, y


def print_top_similar(positive, negative, n):
    global playerset
    global tts
    global map_to_id
    global id_to_map
    if map_to_id is None:
        playerset, tts, map_to_id, id_to_map = get_tts(num_times)

    data = _get_feature_vector(FEATURE_MODEL)

    for mapname in positive:
        if mapname not in map_to_id:
            print(mapname + " not found!")
            return
    for mapname in negative:
        if mapname not in map_to_id:
            print(mapname + " not found!")
            return
    # to sum features on
    map_features = np.zeros(len(data[0]))
    for mapname in positive:
        map_id = mapdata_reduced_map[map_to_id[mapname]]
        map_features += data[map_id]
    for mapname in negative:
        map_id = mapdata_reduced_map[map_to_id[mapname]]
        map_features -= data[map_id]

    # build dict of similar maps:
    similarity = {}
    for i, features in enumerate(data):
        similarity[i] = cosine_similarity(map_features, features)
    sorted_maps = sorted(similarity.items(), key=lambda kv: -kv[1])
    # print(sorted_maps)
    print("Most similar maps to " + str(positive) + " - " + str(negative) + ":")
    n_printed = 0
    i = 0
    while n_printed < n or i == len(data):
        mapname = id_to_map[mapdata_reduced_map_reversed[sorted_maps[i][0]]]
        if mapname not in positive and mapname not in negative:
            print(n_printed, mapname.ljust(25), sorted_maps[i][1])
            n_printed += 1
        i += 1

    sorted_maps_reverse = sorted(similarity.items(), key=lambda kv: kv[1])
    print("\n")
    print("Least similar maps to " + str(positive) + " - " + str(negative) + ":")
    n_printed = 0
    i = 0
    while n_printed < n or i == len(data):
        mapname = id_to_map[mapdata_reduced_map_reversed[sorted_maps_reverse[i][0]]]
        if mapname not in positive and mapname not in negative:
            print(n_printed, mapname.ljust(25), sorted_maps_reverse[i][1])
            n_printed += 1
        i += 1


def get_similar(positive, n):
    global playerset
    global tts
    global map_to_id
    global id_to_map
    if map_to_id is None:
        playerset, tts, map_to_id, id_to_map = get_tts(num_times)

    data = _get_feature_vector(FEATURE_MODEL)

    for mapname in positive:
        if mapname not in map_to_id:
            print(mapname + " not found!")
            return

    # to sum features on
    map_features = np.zeros(len(data[0]))
    for mapname in positive:
        map_id = mapdata_reduced_map[map_to_id[mapname]]
        map_features += data[map_id]

    # build dict of similar maps:
    similarity = {}
    for i, features in enumerate(data):
        similarity[i] = cosine_similarity(map_features, features)
    sorted_maps = sorted(similarity.items(), key=lambda kv: -kv[1])
    # print(sorted_maps)
    # print("Most similar maps to " + str(positive) + " - " + str(negative) + ":")
    n_printed = 0
    i = 0
    similar = []
    while (n_printed < n or n == 0) and i < len(data):
        try:
            mapname = id_to_map[mapdata_reduced_map_reversed[sorted_maps[i][0]]]
            if mapname not in positive:
                # print(n_printed, mapname.ljust(25), sorted_maps[i][1])
                n_printed += 1
                similar.append({"name": mapname, "value": sorted_maps[i][1]})
        except KeyError:
            pass
        i += 1
    return similar


def load_model(class_id=3):
    global player_class
    if player_class == class_id:
        # already loaded
        return
    K.clear_session()
    player_class = class_id
    global modelname
    modelname = f"mapsim_{player_class}_top{num_times}_{nfeatures}f"
    global FEATURE_MODEL
    _gen_training()
    filename = modelname + "_weights.h5"
    FEATURE_MODEL = _init_model(nfeatures, M, P)
    FEATURE_MODEL.load_weights(filename)


def create_model(class_id=3):
    global player_class
    player_class = class_id
    global modelname
    modelname = f"mapsim_{player_class}_top{num_times}_{nfeatures}f"
    # create Skipgram model
    global FEATURE_MODEL
    _gen_training()
    FEATURE_MODEL = _init_model(nfeatures, M, P)
    print(FEATURE_MODEL.summary())


def train_model(class_id=3):
    global player_class
    player_class = class_id
    # train Skipgram model
    global FEATURE_MODEL
    if mapdata_reduced is None:
        _gen_training()
    x, y = _get_dimensions()
    result = FEATURE_MODEL.fit(x=x, y=y, batch_size=5, epochs=10, verbose=1)
    FEATURE_MODEL.save_weights(modelname + "_weights.h5")
