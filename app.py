#!/usr/bin/env python

import traceback

from flask import Flask, render_template

app = Flask(__name__)
app.config["FREEZER_DESTINATION"] = "docs"

from recommend import recommend_player


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/recommend/<int:player_id>/<int:class_id>/")
def player_page(player_id, class_id):
    date = "2022-12-28" # TODO get from db
    try:
        recommendations = recommend_player(player_id, class_id)

        if recommendations is None:
            return render_template(
                "index.html",
                errors=[
                    "Couldn't recommend maps, do you have top times as the selected class?"
                ],
            )

        for rec in recommendations:
            rec["value"] = str(round(rec["value"], 3))

        return render_template("index.html", recommendations=recommendations, date=date)

    except Exception as e:
        traceback.print_exc()
        return render_template(
            "index.html", errors=["Couldn't get recommendations", str(e),], date=date
        )


if __name__ == "__main__":
    app.run("127.0.0.1", "5000", threaded=False)
