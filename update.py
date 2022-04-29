"""
Script for updating tempus database
"""

import os
import map_classification as mc


if __name__ == "__main__":
    try:
        os.remove("tempus.db")
    except FileNotFoundError as e:
        pass

    mc.create_db("tempus")
