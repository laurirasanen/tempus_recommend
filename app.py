#!/usr/bin/env python

import traceback

from flask import Flask, render_template

app = Flask(__name__)

from recommend import recommend_player


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/recommend/<int:player_id>/<int:class_id>")
def recommend(player_id, class_id):
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
            rec["value"] = str(round(rec["value"], 2))

        return render_template("index.html", recommendations=recommendations)

    except Exception as e:
        traceback.print_exc()
        return render_template(
            "index.html", errors=["Couldn't get recommendations", str(e)]
        )


if __name__ == "__main__":
    app.run("127.0.0.1", "5000", threaded=False)
