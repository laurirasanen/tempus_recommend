import sys
import math
import sqlite3

from .api import *


def create_db(name):
    print("using database '%s.db'" % (name))
    maps = get_all()
    users = get_users(maps)
    print("opening database '%s.db'" % (name))
    conn = sqlite3.connect(name + ".db")
    c = conn.cursor()
    print("creating tables")
    # create maps table
    c.execute(
        """CREATE TABLE IF NOT EXISTS maps (id INTEGER PRIMARY KEY NOT NULL, name TEXT, stier INTEGER, dtier INTEGER, svid TEXT, dvid TEXT, authors TEXT)"""
    )
    # create times table
    c.execute(
        """CREATE TABLE IF NOT EXISTS times (id INTEGER PRIMARY KEY NOT NULL, map_id INTEGER, user_id INTEGER, class INTEGER, rank INTEGER, date REAL, duration REAL,
        FOREIGN KEY (map_id) REFERENCES maps (id), FOREIGN KEY (user_id) REFERENCES users (id))"""
    )
    # create users table
    c.execute(
        """CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY NOT NULL, steamid TEXT, name TEXT, srank INTEGER, drank INTEGER)"""
    )

    print("inserting data..")
    for x in range(0, len(maps)):
        # add map to maps table
        c.execute(
            """INSERT OR REPLACE INTO maps (id, name, stier, dtier, svid, dvid, authors) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                maps[x]["map"]["id"],
                maps[x]["map"]["name"],
                maps[x]["map"]["tier_info"]["3"],
                maps[x]["map"]["tier_info"]["4"],
                maps[x]["map"]["videos"]["soldier"],
                maps[x]["map"]["videos"]["demoman"],
                str(maps[x]["map"]["authors"]),
            ),
        )

        for i in range(0, len(maps[x]["times"]["soldier"])):
            # add time to times table
            c.execute(
                """INSERT OR REPLACE INTO times (id, map_id, user_id, class, rank, date, duration) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    maps[x]["times"]["soldier"][i]["id"],
                    maps[x]["map"]["id"],
                    maps[x]["times"]["soldier"][i]["player_info"]["id"],
                    3,
                    maps[x]["times"]["soldier"][i]["rank"],
                    maps[x]["times"]["soldier"][i]["date"],
                    maps[x]["times"]["soldier"][i]["duration"],
                ),
            )
            # add to user to users table
            # this needs to be optimised
            # looping through users is a bad idea..
            user = {}
            for u in users:
                if (
                    u["player_info"]["id"]
                    == maps[x]["times"]["soldier"][i]["player_info"]["id"]
                ):
                    user = u
            if "class_rank_info" in user:
                c.execute(
                    """INSERT OR REPLACE INTO users (id, steamid, name, srank, drank) VALUES (?, ?, ?, ?, ?)""",
                    (
                        user["player_info"]["id"],
                        user["player_info"]["steamid"],
                        user["player_info"]["name"],
                        user["class_rank_info"]["3"]["rank"],
                        user["class_rank_info"]["4"]["rank"],
                    ),
                )

        for i in range(0, len(maps[x]["times"]["demoman"])):
            # add time to times table
            c.execute(
                """INSERT OR REPLACE INTO times (id, map_id, user_id, class, rank, date, duration) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    maps[x]["times"]["demoman"][i]["id"],
                    maps[x]["map"]["id"],
                    maps[x]["times"]["demoman"][i]["player_info"]["id"],
                    4,
                    maps[x]["times"]["demoman"][i]["rank"],
                    maps[x]["times"]["demoman"][i]["date"],
                    maps[x]["times"]["demoman"][i]["duration"],
                ),
            )
            # add to user to users table
            user = {}
            for u in users:
                if (
                    u["player_info"]["id"]
                    == maps[x]["times"]["demoman"][i]["player_info"]["id"]
                ):
                    user = u
            if "class_rank_info" in user:
                c.execute(
                    """INSERT OR REPLACE INTO users (id, steamid, name, srank, drank) VALUES (?, ?, ?, ?, ?)""",
                    (
                        user["player_info"]["id"],
                        user["player_info"]["steamid"],
                        user["player_info"]["name"],
                        user["class_rank_info"]["3"]["rank"],
                        user["class_rank_info"]["4"]["rank"],
                    ),
                )

    conn.commit()
    conn.close()
    print("saved database to '%s.db'" % (name))


def get_tts(num_times=50, player_class=3):
    conn = sqlite3.connect("tempus.db")
    c = conn.cursor()

    c.execute("SELECT id, name FROM maps")
    rows = c.fetchall()
    map_to_id = {}
    id_to_map = {}
    for row in rows:
        # id
        mapid = int(row[0])
        # name
        mapname = str(row[1])
        map_to_id[mapname] = mapid
        id_to_map[mapid] = mapname
    # print(map_to_id)
    # print(id_to_map)

    # initialise all top times
    tts = {}
    for mapid in id_to_map.keys():
        tts[mapid] = [0] * num_times
    # set of people having tts
    playerset = set()

    # get all times
    c.execute(
        "SELECT map_id, user_id, rank FROM times WHERE rank < "
        + str(num_times + 1)
        + " AND class = "
        + str(player_class)
    )
    rows = c.fetchall()
    for row in rows:
        mapid = int(row[0])
        userid = int(row[1])
        rank = int(row[2])
        playerset.add(userid)
        tts[mapid][rank - 1] = userid

    # done loading into memory
    conn.close()
    return playerset, tts, map_to_id, id_to_map


def get_player_tts(player_id, player_class=3):
    conn = sqlite3.connect("tempus.db")
    c = conn.cursor()

    c.execute(
        "SELECT maps.name as map_name, times.rank from maps INNER JOIN times ON maps.id = times.map_id WHERE times.user_id = ? AND times.class = ? AND times.rank <= 10",
        (player_id, player_class),
    )
    rows = c.fetchall()

    tts = []
    for row in rows:
        tts.append({"map_name": row[0], "rank": int(row[1])})
    return tts
