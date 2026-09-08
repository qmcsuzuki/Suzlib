# competitive-verifier: TITLE 幅優先探索 (BFS)

def bfs(g,start):
    """始点から幅優先探索し、訪問順と未到達を -1 とする距離配列を返す。"""
    n = len(g)
    #prev = [-1]*n
    bfs_order = [start]
    dist = [-1]*n
    dist[start] = idx = 0
    while idx < len(bfs_order):
        u = bfs_order[idx]
        for v in g[u]:
            if dist[v] != -1: continue
            dist[v] = dist[u] + 1
            #prev[v] = u
            bfs_order.append(v)
        idx += 1
    return bfs_order, dist #,prev


def BFSmulti(g,starts):
    """複数始点から幅優先探索し、訪問順と最寄りの始点からの距離配列を返す。"""
    n = len(g)
    bfs_order = []
    dist = [-1]*n
    for s in starts:
        if dist[s] != -1: continue
        dist[s] = 0
        bfs_order.append(s)
    idx = 0
    while idx < len(bfs_order):
        u = bfs_order[idx]
        for v in g[u]:
            if dist[v] != -1: continue
            dist[v] = dist[u] + 1
            bfs_order.append(v)
        idx += 1
    return bfs_order, dist
