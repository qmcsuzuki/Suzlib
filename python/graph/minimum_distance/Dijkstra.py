"""
Dijkstra法: 単一始点最短路（距離が正）
g: g[i] = [(子、距離),...]の隣接リスト
start: 始点
返り値 dist: #startからの最短距離
"""

from heapq import *
def dijkstra(g,start):
    n = len(g)
    INF = 1<<61
    dist = [INF]*n
    dist[start] = 0
    q = [(0,start)] #(そこまでの距離、点)
    while q:
        dv,v = heappop(q)
        if dist[v] < dv: continue
        for to, cost in g[v]:
            ncost = dv + cost
            if ncost < dist[to]:
                dist[to] = ncost
                heappush(q, (ncost, to))
    return dist
