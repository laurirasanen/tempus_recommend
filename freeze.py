import time
from flask_frozen import Freezer
from app import app
from map_classification.db import get_players, get_maps

freezer = Freezer(app)


@freezer.register_generator
def player_page():
    players = get_players()

    # yield classes in separate loops so we don't swap models twice per player
    print(
        f"generating {len(players)} soldier player pages (ids: {players[0]['id']} - {players[-1]['id']})"
    )
    x = 0
    time_start = time.time()
    for player in players:
        yield {"player_id": player["id"], "class_id": 3}
        x += 1
        if x % 50 == 0:
            elapsed = time.time() - time_start
            print(
                f"progress: {x}/{len(players)}, elapsed: {round(elapsed)}s, eta: {round((elapsed / x) * len(players) - elapsed)}s"
            )

    print(
        f"generating {len(players)} demoman player pages (ids: {players[0]['id']} - {players[-1]['id']})"
    )
    x = 0
    time_start = time.time()
    for player in players:
        yield {"player_id": player["id"], "class_id": 4}
        x += 1
        if x % 50 == 0:
            elapsed = time.time() - time_start
            print(
                f"progress: {x}/{len(players)}, elapsed: {round(elapsed)}s, eta: {round((elapsed / x) * len(players) - elapsed)}s"
            )


@freezer.register_generator
def map_page():
    maps = get_maps()

    print(
        f"generating {len(maps)} map pages for soldier"
    )
    x = 0
    time_start = time.time()
    for map in maps:
        yield {"map_name": map["name"], "class_id": 3}
        x += 1
        if x % 50 == 0:
            elapsed = time.time() - time_start
            print(
                f"progress: {x}/{len(maps)}, elapsed: {round(elapsed)}s, eta: {round((elapsed / x) * len(maps) - elapsed)}s"
            )

    print(
        f"generating {len(maps)} map pages for demoman"
    )
    x = 0
    time_start = time.time()
    for map in maps:
        yield {"map_name": map["name"], "class_id": 4}
        x += 1
        if x % 50 == 0:
            elapsed = time.time() - time_start
            print(
                f"progress: {x}/{len(maps)}, elapsed: {round(elapsed)}s, eta: {round((elapsed / x) * len(maps) - elapsed)}s"
            )


if __name__ == "__main__":
    freezer.freeze()
