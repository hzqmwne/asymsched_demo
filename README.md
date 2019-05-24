# asymsched_demo

### 安装环境及运行Flask服务器

服务器使用的是Python3环境。
使用virtualenv在虚拟环境中安装Python库依赖。

```bash
virtualenv --no-site-packages venv
source venv/bin/activate
pip install -r asymsched/requirements.txt
```

接下来运行Flask服务器，使用的是调试环境，端口号为5000.
```bash
python3 rest_server.py
```

### API接口介绍

#### 运行asymsched算法一次
---

根据提供的参数运行asymsched算法一次，返回最优的放置策略。

* **url**
/api/asymsched_once

* **请求参数**

包括app的参数，节点间带宽参数和远程访问统计数据。如：
```json
{
  "apps":[
    {
      "tm": 0.0,
      "tt": 50000,
      "clusters": [
        {
          "memories": [200, 400],
          "current_nodes": [0, 1]
        }
      ]
    },
    {
      "tm": 0.0,
      "tt": 50000,
      "clusters": [
        {
          "memories": [30, 300],
          "current_nodes": [2, 3]
        }
      ]
    }
  ],
  "bandwidths":[
    [0, 3000000000, 1000000000, 1000000000],
    [3000000000, 0, 1000000000, 1000000000],
    [1000000000, 1000000000, 0, 7000000000],
    [1000000000, 1000000000, 7000000000, 0]
  ],
  "remote_access": [
     [0, 3000000000, 0, 0],
     [3000000000, 0, 0, 0],
     [0, 0, 0, 5000],
     [0, 0, 5000, 0]
  ]
}
```

* **返回数据**

app的数据，其中包括的新的放置策略。如：
```json


{
  "apps":[
    {
      "tm": 0.0,
      "tt": 50000,
      "clusters": [
        {
          "rbw": 6000000000,
          "weight": 22.515025306174465,
          "memories": [200, 400],
          "origin_nodes": [0, 1],
          "current_nodes": [2, 3]
        }
      ]
    },
    {
      "tm": 0.0,
      "tt": 50000,
      "clusters": [
        {
          "rbw": 10000,
          "weight": 9.210340371976184,
          "orinal_nodes":[]
          "memories": [30, 300],
          "origin_nodes": [2, 3],
          "current_nodes": [0, 1]
        }
      ]
    }
  ],
  "do_migration": true,
  "min_pid": 16,
  "placements": [
    {
      "mm": 0,
      "placements": [
        [[0,1]],
        [[2,3]]
      ],
      "wbw": 264034917044.71335
    }
  ]
}
```

