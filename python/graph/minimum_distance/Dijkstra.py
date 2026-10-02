# competitive-verifier: TITLE ダイクストラ法

"""
Dijkstra法: 単一始点最短路（辺重みは非負、0 も可）
g: g[i] = [(子、距離),...]の隣接リスト
start: 始点
返り値 dist: start からの最短距離。未到達は 1<<61。有限距離はこの値未満を仮定。
時間 O((V+E) log(V+E))、空間 O(V+E)（多重辺も可）。
"""

from heapq import *
def dijkstra(g,start):
    """非負重みの隣接リストから単一始点の最短距離配列を求める。"""
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
