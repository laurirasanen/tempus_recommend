#!/usr/bin/env python

import traceback

from flask import Flask, render_template

app = Flask(__name__)
app.config["FREEZER_DESTINATION"] = "docs"

from recommend import recommend_player, recommend_maps

DB_DATE = "2023-11-16" # TODO get from db

@app.route("/")
def index():
    return render_template("index.html", date=DB_DATE)

@app.route("/player.html")
def player():
    return render_template("player.html", date=DB_DATE)

@app.route("/map.html")
def map():
    return render_template("map.html", date=DB_DATE)


@app.route("/player/<int:player_id>/<int:class_id>/")
def player_page(player_id, class_id):
    try:
        recommendations = recommend_player(player_id, class_id, 50)

        if recommendations is None:
            return render_template(
                "player.html",
                errors=[
                    "Couldn't recommend maps, do you have top 50 times as the selected class?"
                ],
            )

        for rec in recommendations:
            rec["value"] = str(round(rec["value"], 3))

        return render_template("player.html", recommendations=recommendations, date=DB_DATE)

    except Exception as e:
        traceback.print_exc()
        return render_template(
            "player.html", errors=["Couldn't get recommendations", str(e),], date=DB_DATE
        )


@app.route("/map/<string:map_name>/<int:class_id>/")
def map_page(map_name, class_id):
    try:
        recommendations = recommend_maps(map_name, class_id)

        if recommendations is None:
            return render_template(
                "map.html",
                errors=[
                    f"Couldn't find similar maps, does '{map_name}' exist?"
                ],
            )

        for rec in recommendations:
            rec["value"] = str(round(rec["value"], 3))

        return render_template("map.html", recommendations=recommendations, date=DB_DATE)

    except Exception as e:
        traceback.print_exc()
        return render_template(
            "map.html", errors=["Couldn't get similar maps", str(e),], date=DB_DATE
        )


if __name__ == "__main__":
    app.run("127.0.0.1", "5000", threaded=False)
