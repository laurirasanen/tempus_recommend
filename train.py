"""
Script for updating model
"""

import os
import map_classification as mc
import multiprocessing


def train_thread(class_id):
    mc.create_model(class_id)
    mc.train_model(class_id)


if __name__ == "__main__":
    try:
        os.remove("mapsim_3_top50_600f_weights.h5")
    except FileNotFoundError as e:
        pass

    try:
        os.remove("mapsim_4_top50_600f_weights.h5")
    except FileNotFoundError as e:
        pass

    # train soldier and demoman models in parallel
    class_ids = [3, 4]
    pool = multiprocessing.Pool(processes=os.cpu_count())
    pool.map(train_thread, class_ids)
