""" 本文件定义了一些数据模型类 """

class Cluster:
    """ 一个cluster同一个app之中访问相同的内存的线程集合 """

    def __init__(self):
        self.rbw = 0 # 访问远程节点的带宽
        self.weight = 0 # cluster的权重，通常为log(rbw)
        self.memories = [] # cluster中每个节点使用的内存大小
        self.origin_nodes = [] # cluster上一次分配的节点
        self.current_nodes = [] # 当前cluster分配的节点

    def set_data(self, data):
        """ 从字典数据从加载数据到本对象
        """
        assert 'memories' in data
        assert 'current_nodes' in data
        assert len(data['memories']) == len(data['current_nodes'])
        self.memories = data['memories']
        self.current_nodes = data['current_nodes']

    def serialize(self):
        ''' 序列化成字典数据
        '''

        return {
            "rbw": self.rbw,
            "weight": self.weight,
            "memories": self.memories,
            "origin_nodes": self.origin_nodes,
            "current_nodes": self.current_nodes
        }

class App:
    """ app中包含了多个cluster，通常设为1个 """

    def __init__(self):
        self.tm = 0.0 # time already spent migrating memory
        self.tt = 0.0 # dynamic running time of the application
        self.clusters = []

    def set_data(self, data):
        """ 从字典数据从加载数据到本对象
        """

        assert 'tm' in data
        assert 'tt' in data
        assert 'clusters' in data

        self.tm = data['tm']
        self.tt = data['tt']
        self.clusters = []

        for cluster_id, cluster_data in enumerate(data['clusters']):
            self.clusters.append(Cluster())
            self.clusters[cluster_id].set_data(cluster_data)

    def serialize(self):
        ''' 序列化成字典数据
        '''

        return {
            "tm": self.tm,
            "tt": self.tt,
            "clusters": list(map(Cluster.serialize, self.clusters))
        }

class Placement:
    """ placement包含了相关的统计数据及具体的放置策略 """

    def __init__(self, num_apps):
        self.wbw = 0
        self.mm = 0
        self.placements = [[] for i in range(num_apps)]

    def serialize(self):
        ''' 序列化成字典数据
        '''

        return {
            "wbw": self.wbw,
            "mm": self.mm,
            "placements": self.placements
        }
