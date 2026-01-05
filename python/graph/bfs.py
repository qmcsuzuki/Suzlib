# verification-helper: TITLE 幅優先探索 (BFS)

def bfs(g,start):
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
