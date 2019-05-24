""" 本文件定义了一些数据模型类 """

class Cluster:
    """ 一个cluster同一个app之中访问相同的内存的线程集合 """

    def __init__(self):
        self.rbw = 0 # 访问远程节点的带宽
        self.weight = 0 # cluster的权重，通常为log(rbw)
        self.num_nodes = 0 # 需要使用到的节点
        self.memories = [] # cluster中每个节点使用的内存大小
        self.origin_nodes = [] # cluster上一次分配的节点
        self.current_nodes = [] # 当前cluster分配的节点

class App:
    """ app中包含了多个cluster，通常设为1个 """
    def __init__(self):
        self.tm = 0.0 # time already spent migrating memory
        self.tt = 0.0 # dynamic running time of the application
        self.num_cluster = 0
        self.clusters = []

class Placement:
    """ placement包含了相关的统计数据及具体的放置策略 """

    def __init__(self, num_apps):
        self.wbw = 0
        self.mm = 0
        self.placements = [[] for i in range(num_apps)]
