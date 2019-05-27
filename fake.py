import json
import random
import itertools

interconnects = [
    [0, 5600, 4300, 3800, 3000, 2900, 3000, 3000],
    [5600, 0, 3800, 4300, 3000, 2900, 2900, 3000],
    [3000, 1900, 0, 5600, 3000, 4300, 1900, 1900],
    [1900, 3000, 5600, 0, 3000, 3000, 1900, 1900],
    [3000, 3000, 3000, 3000, 0, 5600, 4300, 1900],
    [1900, 1900, 4300, 3000, 5600, 0, 4300, 3000],
    [4300, 3800, 3000, 3000, 3000, 1900, 0, 5600],
    [1900, 3000, 3800, 3800, 2900, 3000, 5600, 0]
]
fake_n = 10
app_n = 4
node_n = 8
core_per_node = 8

fake_i = 0
fakes = []
while fake_i != fake_n:
    apps = []
    for app_i in range(app_n):
        apps.append({
            "name": "app" + str(app_i),
            "thread_n": random.randint(2, 4) * core_per_node,
            "total_memory": 2 ** random.randint(8, 13),
            "compute_per_thread": random.randint(1, 10),
            # memory_access_per_thread: 4 GB ~ 16 GB
            "memory_access_per_thread": 2 ** random.randint(12, 14),
            "remote_memory_ratio": random.random()
        })

    if sum([app["thread_n"] // core_per_node for app in apps]) > node_n:
        # print("apps need too many nodes, try again")
        continue

    best = {
        "placement": None,
        "total_time": None,
        "app_times": []
    }
    worst = {
        "placement": None,
        "total_time": None,
        "app_times": []
    }

    for placement in itertools.permutations(range(node_n)):
        node_visited = 0
        total_time = 0
        app_times = []
        for app_i in range(app_n):
            app_node_n = apps[app_i]["thread_n"] // core_per_node
            app_time = 0
            for app_node_i in range(app_node_n):
                thread_remote_access = apps[app_i]["memory_access_per_thread"] * \
                    apps[app_i]["remote_memory_ratio"]
                thread_remote_bandwidth = interconnects[placement[node_visited +
                                                                  app_node_i]][placement[node_visited + (app_node_i + 1) % app_node_n]]
                thread_time = thread_remote_access / \
                    thread_remote_bandwidth + apps[app_i]["compute_per_thread"]
                app_time = max(app_time, thread_time)
            app_times.append(app_time)
            total_time = max(total_time, app_time)
            node_visited += app_node_n

        if worst["total_time"] is None or total_time > worst["total_time"]:
            worst["placement"] = placement
            worst["total_time"] = total_time
            worst["app_times"] = app_times
        if best["total_time"] is None or total_time < best["total_time"]:
            best["placement"] = placement
            best["total_time"] = total_time
            best["app_times"] = app_times

    asymsched = {
        "total_time": None,
        "app_times": []
    }
    for app_i in range(app_n):
        asymsched["app_times"].append(
            best["app_times"][app_i] * (0.8 + random.random() * 0.3))
    asymsched["total_time"] = max(asymsched["app_times"])

    fakes.append({
        "apps": apps,
        "best": best,
        "worst": worst,
        "asymsched": asymsched
    })
    fake_i += 1
    print(fake_i)

print(json.dumps(fakes, indent=4))
