# competitive-verifier: TITLE 木の直径（中心取得・中心追加）

from collections import deque

def diameter(g):
    def bfs(start):  # start からの最遠頂点（の1つ）と dist を返す
        dist = [-1] * len(g)
        q = deque([start])
        dist[start] = 0
        while q:
            v = q.popleft()
            for c in g[v]:
                if dist[c] >= 0:
                    continue
                dist[c] = dist[v] + 1
                q.append(c)
        return v, dist

    v0, _ = bfs(0)
    v1, dist = bfs(v0)

    d = dv = dist[v1]
    m0 = d // 2
    m1 = d - m0
    v = v1
    while True:
        if dv == m0: c0 = v
        if dv == m1: c1 = v
        if v == v0: break
        for u in g[v]:
            if dist[u] == dv - 1:
                v = u
                break
        dv -= 1
    # v0,v1 が直径の両端
    # c0,c1 が中心を挟む頂点 (c0=c1 なら、その点が中心)
    return v0, v1, c0, c1, d

def modify_graph_add_new_center(g, c0, c1, d):
    """
    木 g (隣接リスト, 無向) で、辺 (c0,c1) を分割して新頂点 x を挿入する。
    返り値: (v,newn,newd,flag): 新頂点 x の index,新しい頂点数、新しい直径の長さ, 追加されたか
    g は破壊的に変更される
    """
    n = len(g)
    if c0 == c1:
        return c0,n,d,0  # 直径が偶数なら変更の必要なし
    # 元の辺を削除
    g[c0].remove(c1);
    g[c1].remove(c0)
    # 辺を追加
    g.append([c0,c1])
    g[c0].append(n)
    g[c1].append(n)
    return n,n+1,d+1,1
