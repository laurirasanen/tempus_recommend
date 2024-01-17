import map_classification as mc


def recommend_player(player_id, class_id, max_rank):
    mc.load_model(class_id)
    tts = mc.get_player_tts(player_id, class_id, max_rank)

    if len(tts) == 0:
        return None

    # get recommendations and apply weight
    recommendations = {}
    for time in tts:
        similar = mc.get_similar(time["map_name"])
        for s in similar:
            if s["name"] in recommendations:
                recommendations[s["name"]] += s["value"]
            else:
                recommendations[s["name"]] = s["value"]

    recommendations_list = []
    for k, v in recommendations.items():
        recommendations_list.append({"name": k, "value": v})
    recommendations_list.sort(key=lambda r: -r["value"])
    return recommendations_list


def recommend_maps(map_name, class_id):
    mc.load_model(class_id)
    similar = mc.get_similar(map_name)
    return similar
