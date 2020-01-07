from fastapi import FastAPI

from recommend import recommend_player


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/recommend")
def read_item(player_id: int, class_id: int):
    return recommend_player(player_id, class_id)