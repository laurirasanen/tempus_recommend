import sys
import math
import sqlite3
from pprint import pprint

def get_tts(num_times=50, player_class=3):
    conn = sqlite3.connect("tempus.db")
    c = conn.cursor()

    c.execute("SELECT id, name, stier, dtier FROM maps")
    rows = c.fetchall()
    maps = {}
    for row in rows:
        mapid = int(row[0])
        mapname = str(row[1])
        stier = int(row[2])
        dtier = int(row[3])
        maps[mapid] = {
            "id": mapid,
            "name": mapname,
            "stier": stier,
            "dtier": dtier,
            "tts": [0] * num_times
        }

    c.execute(
        "SELECT map_id, user_id, rank, duration FROM times WHERE rank < "
        + str(num_times + 1)
        + " AND class = "
        + str(player_class)
    )
    rows = c.fetchall()
    for row in rows:
        mapid = int(row[0])
        userid = int(row[1])
        rank = int(row[2])
        duration = float(row[3])
        maps[mapid]["tts"][rank - 1] = {
            "userid": userid,
            "duration": duration,
            "rank": rank
        }

    conn.close()
    return maps

if __name__ == "__main__":
    num_times = 1
    class_index = 4
    tiers = [0, 1, 2, 3, 4, 5, 6]

    maps = get_tts(num_times, class_index)
    wrs = []
    for id in maps:
        tier = maps[id]["stier"]
        if class_index == 4:
            tier = maps[id]["dtier"]
        if tier not in tiers:
            continue
        wr = maps[id]["tts"][0]
        if wr == 0:
            continue
        wrs.append({
            "id": id,
            "name": maps[id]["name"],
            "time": wr["duration"]
        })
    wrs.sort(key=lambda p: p["time"], reverse=True)
    pprint(wrs)
            
