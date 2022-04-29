import requests
import time
import math
from operator import itemgetter
import multiprocessing


apiurl = "https://tempus.xyz/api/"
headers = {"Accept": "application/json"}
time_start = time.time()
requests_sent = None
top_times = 50


def get_all():
    global requests_sent
    requests_sent = multiprocessing.Value("i", 0)
    maps = get_maps()
    if "error" in maps:
        print("error getting maps")
        print(maps.error)
        return

    # check times on 4 maps simultaneously to achieve some asynchronosity
    # we get can only get 50 runs at a time,
    # and we need to wait the for response to determine if we need to get another 50 or if we are done
    pool = multiprocessing.Pool(
        processes=4, initializer=init, initargs=(requests_sent,)
    )
    all_maps = []
    # maps = maps[0:2]
    for i in pool.imap(maps_thread, maps):
        all_maps.append(i)
        time_passed = math.floor(time.time() - time_start)
        time_remaining = math.floor(
            (time_passed / (len(all_maps))) * (len(maps) - len(all_maps))
        )
        if time_passed > 60:
            time_passed = (
                str(math.floor(time_passed / 60)) + "m" + str(time_passed % 60) + "s"
            )
        else:
            time_passed = str(time_passed) + "s"
        if time_remaining > 60:
            time_remaining = (
                str(math.floor(time_remaining / 60))
                + "m"
                + str(time_remaining % 60)
                + "s"
            )
        else:
            time_remaining = str(time_remaining) + "s"
        print(
            "progress: %d/%d maps, time passed: %s (estimated remaining: %s)"
            % (len(all_maps), len(maps), time_passed, time_remaining)
        )
        if len(all_maps) == len(maps):
            print(
                "finished api requests in %s, requests sent: %d (%f req/s)"
                % (
                    time_passed,
                    requests_sent.value,
                    requests_sent.value / math.floor(time.time() - time_start),
                )
            )

    return all_maps


# define requests_sent counter for later use in threads
def init(args):
    global requests_sent
    requests_sent = args


def maps_thread(_map):
    times = get_times(_map["id"])
    return {"map": _map, "times": times}


def get_maps():
    r = requests.get(apiurl + "maps/detailedList", headers=headers)
    global requests_sent
    with requests_sent.get_lock():
        requests_sent.value += 1
    return r.json()


def get_times(_map):
    i = 1
    times = {"soldier": [], "demoman": []}
    while True:
        json_times = loop_times(_map, i)
        if "error" in json_times:
            print("error looping times")
            print(json_times["error"])
            return times

        if (
            "results" in json_times
            and "soldier" in json_times["results"]
            and "demoman" in json_times["results"]
        ):
            for x in range(0, len(json_times["results"]["soldier"])):
                json_times["results"]["soldier"][x]["rank"] = i + x
                times["soldier"].append(json_times["results"]["soldier"][x])
            for x in range(0, len(json_times["results"]["demoman"])):
                json_times["results"]["demoman"][x]["rank"] = i + x
                times["demoman"].append(json_times["results"]["demoman"][x])

            if (
                len(json_times["results"]["demoman"]) < 50
                and len(json_times["results"]["soldier"]) < 50
            ):
                return times

            i += 50
            if i > top_times:
                return times
        else:
            return times


def loop_times(_map, i):
    r = requests.get(
        apiurl
        + "maps/id/"
        + str(_map)
        + "/zones/typeindex/map/1/records/list?start="
        + str(i),
        headers=headers,
    )
    global requests_sent
    with requests_sent.get_lock():
        requests_sent.value += 1
    return r.json()


def get_users(maps):
    userids = []
    for m in maps:
        for t in m["times"]["soldier"]:
            if t["player_info"]["id"] not in userids:
                userids.append(t["player_info"]["id"])
        for t in m["times"]["demoman"]:
            if t["player_info"]["id"] not in userids:
                userids.append(t["player_info"]["id"])
    global requests_sent
    with requests_sent.get_lock():
        requests_sent.value = 0
    global time_start
    time_start = time.time()
    pool = multiprocessing.Pool(
        processes=4, initializer=init, initargs=(requests_sent,)
    )
    all_users = []
    for i in pool.imap(user_thread, userids):
        all_users.append(i)
        time_passed = math.floor(time.time() - time_start)
        time_remaining = math.floor(
            (time_passed / (len(all_users))) * (len(userids) - len(all_users))
        )
        if time_passed > 60:
            time_passed = (
                str(math.floor(time_passed / 60)) + "m" + str(time_passed % 60) + "s"
            )
        else:
            time_passed = str(time_passed) + "s"
        if time_remaining > 60:
            time_remaining = (
                str(math.floor(time_remaining / 60))
                + "m"
                + str(time_remaining % 60)
                + "s"
            )
        else:
            time_remaining = str(time_remaining) + "s"
        print(
            "progress: %d/%d users, time passed: %s (estimated remaining: %s)"
            % (len(all_users), len(userids), time_passed, time_remaining)
        )
        if len(all_users) == len(userids):
            print(
                "finished getting users in %s, requests sent: %d (%f req/s)"
                % (
                    time_passed,
                    requests_sent.value,
                    requests_sent.value / math.floor(time.time() - time_start),
                )
            )

    return all_users


def user_thread(user_id):
    r = requests.get(apiurl + "players/id/" + str(user_id) + "/rank", headers=headers)
    global requests_sent
    with requests_sent.get_lock():
        requests_sent.value += 1
    return r.json()
