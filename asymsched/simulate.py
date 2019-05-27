# coding:utf8

import random
import itertools
import copy

import asymsched

class Machine:
    def __init__(self):
        pass
    def __init__(self, b):
        self.bandwidth = b

class Thread:
    def __init__(self):
        pass
    def __init__(self, n, mp, ct, ctd, ma):
        self.node = n
        self.memory_placement = mp
        self.compute_time = ct
        self.compute_time_done = ctd
        self.memory_access_remainder = ma
        self.time_remainder = 0

        self.finishtime = None

class Process:
    def __init__(self):
        pass
    def __init__(self, ts):
        self.threads = ts

class Event:
    def __init__(self):
        pass
    def __init__(self, ti, ty, th):
        self.timer = ti
        self.type = ty
        self.thread = th

PLACEMENT_UPDATE = 0
THREAD_FINISHED = 1

def calculate_thread_finish_events(machine, processes, timer):
    events = []
    for p in processes:
        for t in p.threads:
            total_memory_access_latency = 0
            for node,access in t.memory_access_remainder.items():
                total_memory_access_latency += access*1.0/machine.bandwidth[t.node][node]
                # print("memory access latency: %f"%total_memory_access_latency)
            # print(timer,t.compute_time_done,total_memory_access_latency)
            e = Event(timer+t.compute_time-t.compute_time_done+total_memory_access_latency, THREAD_FINISHED, t)
            events.append(e)
    return events

def gen_placement_update_events(update_interval, timer):
    events = []
    e = Event(timer+update_interval, PLACEMENT_UPDATE, None)
    events.append(e)
    return events

def new_event_list(machine, processes, update_interval, timer):
    events = calculate_thread_finish_events(machine, processes, timer)+gen_placement_update_events(update_interval, timer)
    events.sort(key=lambda e:e.timer)
    return events

def update_progess(machine, processes, duration):
    if duration == 0:
        return
    for p in processes:
        for t in p.threads:
            memory_access_latency = 0
            for node,access in t.memory_access_remainder.items():
                memory_access_latency += access*1.0/machine.bandwidth[t.node][node]
            cputime_duration = duration*(t.compute_time-t.compute_time_done)*1.0/(t.compute_time-t.compute_time_done+memory_access_latency)
            t.compute_time_done += cputime_duration
            new_memory_access = {}
            for node,access in t.memory_access_remainder.items():
                new_memory_access[node] = access-access*duration*1.0/t.compute_time
            t.memory_access_remainder = new_memory_access

def run_placement(machine, processes):
    remote_access = [[0 for j in range(len(machine.bandwidth[0]))] for i in range(len(machine.bandwidth))]
    apps = []
    for p in processes:
        c = asymsched.Cluster()
        c.current_nodes = []
        c.memories = []
        total_compute_time = 0
        for t in p.threads:
            for node,access in t.memory_access_remainder.items():
                remote_access[t.node][node] = access
            total_compute_time += t.compute_time
            c.current_nodes.append(t.node)
            c.memories.append(t.memory_placement)
        a = asymsched.App()
        a.tt = total_compute_time*1.0/len(p.threads)
        a.clusters = [c]
        apps.append(a)
##    print(remote_access)
##    print(apps[0].tt)
##    print(apps[0].clusters[0].memories)
##    print(apps[0].clusters[0].current_nodes)
##    print(apps[1].tt)
##    print(apps[1].clusters[0].memories)
##    print(apps[1].clusters[0].current_nodes)
    _, _, min_pid, do_migration = asymsched.asymsched(apps, machine.bandwidth, remote_access)
    # print(min_pid, do_migration)
    if not do_migration:
        return None,None
    migration = {}
    migration_time = 0
    for app in apps:
        for cluster in app.clusters:
##            print(cluster.origin_nodes, "==>", cluster.current_nodes)
            for i in range(len(cluster.origin_nodes)):
                ori = cluster.origin_nodes[i]
                cur = cluster.current_nodes[i]
                if ori != cur:
                    migration[ori] = cur
                    migration_time += cluster.memories[i]*1.0/machine.bandwidth[ori][cur]
    return migration, migration_time

def simulation(machine, processes, print_result = 1):
    placement_update_interval = 20000
    timer = 0
    final_timer = 0
    # random.shuffle(processes)
    events = new_event_list(machine, processes, placement_update_interval, timer)
    while 1:
        if len(events) == 0:
            # print("finish time:",timer)
            final_timer = timer
            break
        latest_event = events.pop(0)
        duration = latest_event.timer - timer
        timer = latest_event.timer
        # print("time:",timer)
        update_progess(machine, processes, duration)
        if latest_event.type == THREAD_FINISHED:
            # ensure_finished
            latest_event.thread.finishtime = timer
            pass
        elif latest_event.type == PLACEMENT_UPDATE:
            migration, migration_time = run_placement(machine, processes)
            if migration is None:
                continue
            for p in processes:
                for t in p.threads:
                    t.compute_time_done += migration_time
                    t.node = migration[t.node]
                    new_memory_access = {}
                    for node,access in t.memory_access_remainder.items():
                        new_memory_access[migration[node]] = access-access*duration*1.0/t.compute_time
                    t.memory_access_remainder = new_memory_access
            timer += migration_time
            events = new_event_list(machine, processes, placement_update_interval, timer)
    for i,p in enumerate(processes):
        max_time = -1
        for t in p.threads:
            max_time = t.finishtime if t.finishtime > max_time else max_time
        if print_result:
            print("process",i,"finish time:",max_time)
    if print_result:
        print("finish time:",final_timer)
    return final_timer

def simulation_nomigration(machine, processes, print_result = 1):
    # random.shuffle(processes)
    timer = 0
    final_timer = 0
    events = calculate_thread_finish_events(machine, processes, timer)
    events.sort(key=lambda e:e.timer)
    while 1:
        if len(events) == 0:
            # print("finish time:",timer)
            final_timer = timer
            break
        latest_event = events.pop(0)
        duration = latest_event.timer
        timer = latest_event.timer
        update_progess(machine, processes, duration)
        if latest_event.type == THREAD_FINISHED:
            # ensure_finished
            latest_event.thread.finishtime = timer
            pass
        elif latest_event.type == PLACEMENT_UPDATE:
            assert(0)
    for i,p in enumerate(processes):
        max_time = -1
        for t in p.threads:
            max_time = t.finishtime if t.finishtime > max_time else max_time
        if print_result:
            print("process",i,"finish time:",max_time)
    if print_result:
        print("finish time:",final_timer)
    return final_timer

def find_best_and_worse(machine, processes):
    best_situation_processes = None
    best_finishtime = 0x7fffffff
    worse_situation_processes = None
    worse_finishtime = -1
    node_count = len(machine.bandwidth)

    thread_count = 0
    origin_placement = []
    for p in processes:
        for t in p.threads:
            thread_count += 1
            origin_placement.append(t.node)

    all_placements = [per for per in itertools.permutations(range(node_count),thread_count)]

    for placement in all_placements:
        migration = {}
        for i in range(len(origin_placement)):
            migration[origin_placement[i]] = placement[i]
        processes_copy = copy.deepcopy(processes)
        
        for p in processes_copy:
            for t in p.threads:
                t.node = migration[t.node]
                new_memory_access = {}
                for node,access in t.memory_access_remainder.items():
                    new_memory_access[migration[node]] = access
                t.memory_access_remainder = new_memory_access
        processes_copy_backup = copy.deepcopy(processes_copy)

        finishtime = simulation_nomigration(machine, processes_copy, 0)    #
        
        if finishtime < best_finishtime:
            best_finishtime = finishtime
            best_situation_processes = copy.deepcopy(processes_copy_backup)
        if finishtime > worse_finishtime:
            worse_finishtime = finishtime
            worse_situation_processes = copy.deepcopy(processes_copy_backup)

    return best_situation_processes, worse_situation_processes

def test1():
    bandwidth = [
        [0, 3000000000, 1000000000, 1000000000],
        [3000000000, 0, 1000000000, 1000000000],
        [1000000000, 1000000000, 0, 7000000000],
        [1000000000, 1000000000, 7000000000, 0]
    ]

    machine = Machine(bandwidth)
    processes = []
    
    threads = []
    t = Thread(0, 200, 100000, 0, {1:3000000000})
    threads.append(t)
    
    t = Thread(1, 400, 100000, 0, {0:3000000000})
    threads.append(t)
    p = Process(threads)
    processes.append(p)

    threads = []
    t = Thread(2, 30, 100000, 0, {3:5000})
    threads.append(t)
    t = Thread(3, 300, 100000, 0, {2:5000})
    threads.append(t)
    p = Process(threads)
    processes.append(p)

    best_placement, worse_placement = find_best_and_worse(machine, processes)

    print("test1:")
    simulation(machine, processes)
    simulation_nomigration(machine, best_placement)
    simulation_nomigration(machine, worse_placement)


def test_migration():
    bandwidth = [
        [0, 3000000000, 1000000000, 1000000000],
        [3000000000, 0, 1000000000, 1000000000],
        [1000000000, 1000000000, 0, 7000000000],
        [1000000000, 1000000000, 7000000000, 0]
    ]
    machine = Machine(bandwidth)
    processes = []
    
    threads = []
    t = Thread(0, 200, 100000, 0, {1:3000000000})
    threads.append(t)
    
    t = Thread(1, 400, 100000, 0, {0:3000000000})
    threads.append(t)
    p = Process(threads)
    processes.append(p)

    threads = []
    t = Thread(2, 30, 100000, 0, {3:5000})
    threads.append(t)
    t = Thread(3, 300, 100000, 0, {2:5000})
    threads.append(t)
    p = Process(threads)
    processes.append(p)

    #simulation_nomigration(machine, processes)
    simulation(machine, processes)

def test_best():
    bandwidth = [
        [0, 3000000000, 1000000000, 1000000000],
        [3000000000, 0, 1000000000, 1000000000],
        [1000000000, 1000000000, 0, 7000000000],
        [1000000000, 1000000000, 7000000000, 0]
    ]
    machine = Machine(bandwidth)
    processes = []
    
    threads = []
    t = Thread(2, 200, 100000, 0, {3:3000000000})
    threads.append(t)
    
    t = Thread(3, 400, 100000, 0, {2:3000000000})
    threads.append(t)
    p = Process(threads)
    processes.append(p)

    threads = []
    t = Thread(0, 30, 100000, 0, {1:5000})
    threads.append(t)
    t = Thread(1, 300, 100000, 0, {0:5000})
    threads.append(t)
    p = Process(threads)
    processes.append(p)

    simulation_nomigration(machine, processes)
    

def test_worse():
    bandwidth = [
        [0, 3000000000, 1000000000, 1000000000],
        [3000000000, 0, 1000000000, 1000000000],
        [1000000000, 1000000000, 0, 7000000000],
        [1000000000, 1000000000, 7000000000, 0]
    ]
    machine = Machine(bandwidth)
    processes = []
    
    threads = []
    t = Thread(0, 200, 100000, 0, {1:3000000000})
    threads.append(t)
    
    t = Thread(1, 400, 100000, 0, {0:3000000000})
    threads.append(t)
    p = Process(threads)
    processes.append(p)

    threads = []
    t = Thread(2, 30, 100000, 0, {3:5000})
    threads.append(t)
    t = Thread(3, 300, 100000, 0, {2:5000})
    threads.append(t)
    p = Process(threads)
    processes.append(p)

    simulation_nomigration(machine, processes)
    

"""
测试数据与asymsched.py相同
两个进程，每个进程使用两个node
node 0和1的bandwidth大，node 2和3的bandwidth小
进程0的两个线程access大，进程0的两个线程access小

test_best：进程0使用node0和1，进程1使用node2和3
test_worse：进程0使用node2和3，进程1使用node0和1
test_migration：worse的情况加上算法

输出最后一个线程运行结
束的时间
"""
if __name__ == "__main__":
    test1()
##    print("migration:")
##    test_migration()
##    print("best placement:")
##    test_best()
##    print("worse placement:")
##    test_worse()

bandwidth = [    # bytes/s
    [0, 56, 43, 38, 30, 29, 30, 30],
    [56, 0, 38, 43, 30, 29, 29, 30],
    [30, 19, 0, 56, 30, 43, 19, 19],
    [19, 30, 56, 0, 30, 30, 19, 19],
    [30, 30, 30, 30, 0, 56, 43, 19],
    [19, 19, 43, 30, 56, 0, 43, 30],
    [43, 38, 30, 30, 30, 19, 0, 56],
    [19, 30, 38, 38, 29, 30, 56, 0],
]
    
