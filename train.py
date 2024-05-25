"""
Script for updating model
"""

import os
import map_classification as mc
import multiprocessing


def train_thread(class_id):
    try:
        os.remove(f"mapsim_{class_id}_top50_600f.weights.h5")
    except FileNotFoundError as e:
        pass
    mc.create_model(class_id)
    mc.train_model(class_id)


if __name__ == "__main__":
    # FIXME: soldier model never finishes in parallel
    # not enough memory? :(

    # train soldier and demoman models in parallel
    # class_ids = [3, 4]
    # pool = multiprocessing.Pool(processes=os.cpu_count())
    # pool.map(train_thread, class_ids)
    train_thread(3)
    train_thread(4)
