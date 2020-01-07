"""
Script for updating tempus database and model
"""

import os
import map_classification as mc


def __main__():
    os.remove("tempus.db")
    os.remove("mapsim_3_top50_600f_weights.h5")
    os.remove("mapsim_4_top50_600f_weights.h5")

    mc.create_db("tempus.db")

    # soldier
    mc.create_model(3)
    mc.train_model(3)

    # demoman
    mc.create_model(4)
    mc.train_model(4)
