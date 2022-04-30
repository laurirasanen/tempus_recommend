import time
from flask_frozen import Freezer
from app import app
from map_classification.db import get_players

freezer = Freezer(app)


@freezer.register_generator
def player_page():
    players = get_players()
    print(
        f"generating {len(players)} player pages (ids: {players[0]['id']} - {players[-1]['id']})"
    )
    x = 0
    time_start = time.time()
    for player in players:
        yield {"player_id": player["id"], "class_id": 3}
        yield {"player_id": player["id"], "class_id": 4}
        x += 1
        if x % 50 == 0:
            elapsed = time.time() - time_start
            print(
                f"progress: {x}/{len(players)}, elapsed: {round(elapsed)}s, eta: {round((elapsed / x) * len(players) - elapsed)}s"
            )


if __name__ == "__main__":
    freezer.freeze()
