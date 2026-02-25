# competitive-verifier: TITLE オイラー路

"""
（頂点辞書順最小の）オイラー路を求める
Eulerian_trail_directed(n,edges): 有向
Eulerian_trail_undirected(n,edges): 無向
_find_trail: 内部関数
"""

def _find_trail(g, start, base, m):
    """
    g[v]: グラフ (to*base + eid), 破壊される
    """
    used = [False] * m  # 辺 eid を使ったか
    st_v = [start]
    st_e = [-1]
    out_v = []
    out_e = []

    while st_v:
        v = st_v[-1]
        while g[v] and used[g[v][-1]%base]: # 使った辺は捨てる
            g[v].pop()

        if g[v]:
            to, eid = divmod(g[v].pop(), base)
            used[eid] = True
            st_v.append(to)
            st_e.append(eid)
        else:
            out_v.append(st_v.pop())
            out_e.append(st_e.pop())
    out_e.pop()
    return out_v[::-1], out_e[::-1]


def Eulerian_trail_directed(n, edges):
    """
    n: 頂点数
    edges: 有向辺
    returns: (ok, vertices, edge_ids)
    """
    assert n > 0
    m = len(edges)
    if m == 0:  # 辺が 0 なら、任意の長さ 0 のパスが OK
        return True, [0], []

    degdiff = [0]*n  # outdeg - indeg
    min_u = n+1 # outdeg > 0 となる最小の点番号
    for (u, v) in edges:
        degdiff[u] += 1
        degdiff[v] -= 1
        min_u = min(min_u, u)

    start = end = -1
    for v, d in enumerate(degdiff):
        if d == 1:
            if start != -1:
                return False, [], []
            start = v
        elif d == -1:
            if end != -1:
                return False, [], []
            end = v
        elif d != 0:
            return False, [], []

    # 閉路ができる場合、辺がある頂点を始点に選ぶ
    if start == -1:
        start = min_u

    base = m + 1
    g = [[] for _ in range(n)]
    for eid, (u, v) in enumerate(edges):
        g[u].append(v * base + eid)

    # 頂点順で辞書順最小のため、降順ソート（pop() で最小を取り出す）
    for lst in g:
        lst.sort(reverse=True)

    vertices, edge_ids = _find_trail(g, start, base, m)
    if len(edge_ids) != m or len(vertices) != m + 1:
        return False, [], []
    return True, vertices, edge_ids


def Eulerian_trail_undirected(n, edges):
    """
    n: 頂点数
    edges: 無向辺
    returns: (ok, vertices, edge_ids)
    """
    assert n > 0
    m = len(edges)
    if m == 0:  # 辺が 0 なら、任意の長さ 0 のパスが OK
        return True, [0], []

    deg = [0]*n
    min_u = n+1
    for (u, v) in edges:
        deg[u] += 1
        deg[v] += 1
        min_u = min(min_u, u, v)

    odd = [v for v in range(n) if deg[v] & 1]
    if len(odd) == 2:
        start = odd[0]  # 奇数次数の片方から始める
    elif len(odd) == 0: # 閉路ができる場合、辺がある頂点を始点に選ぶ
        start = min_u
    else:
        return False, [], []

    base = m + 1
    g = [[] for _ in range(n)]
    for eid, (u, v) in enumerate(edges):
        g[u].append(v*base + eid)
        g[v].append(u*base + eid)

    # 頂点順で辞書順最小のため、降順ソート（pop() で最小を取り出す）
    for lst in g:
        lst.sort(reverse=True)

    vertices, edge_ids = _find_trail(g, start, base, m)
    if len(edge_ids) != m or len(vertices) != m + 1:
        return False, [], []
    return True, vertices, edge_ids
