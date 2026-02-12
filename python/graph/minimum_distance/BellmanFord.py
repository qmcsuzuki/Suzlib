"""
dist: start からの距離の配列
ただし未到達には INF, 負回路から行ける道には -INF が格納

INF_inner の値に注意
"""

def Bellman_Ford(g,start):
    INF_inner = INF # INF はグローバルに設定する
    n = len(g)
    dist = [INF_inner]*n
    dist[start] = 0
    for i in range(2*n):
        updated = False
        for v in range(n):
            if dist[v] == INF_inner: continue
            for to, cost in g[v]:
                if dist[to] <= dist[v] + cost or dist[to] == -INF_inner: continue
                dist[to] = (dist[v] + cost) if i < n else -INF_inner
                updated = True
        if not updated: break
    return dist

# https://atcoder.jp/contests/abc137/submissions/49837093
