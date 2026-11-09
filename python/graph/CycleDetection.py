# competitive-verifier: TITLE 有向・無向グラフの閉路検出・復元

"""
Usage:
    ok, vertices, edge_ids = find_cycle_directed(n, edges)
    ok, vertices, edge_ids = find_cycle_undirected(n, edges)

edges は (u, v) のリストで、添字が辺番号。入力は変更しない。
成功時は始点を末尾にも含む頂点列と辺番号列を返す。
vertices[0] == vertices[-1], len(vertices) == len(edge_ids) + 1。
始点と終点以外に頂点の重複がなく、辺の重複もない閉路を一つ返す。
閉路がなければ (False, [], [])。辺が 0 本の場合も閉路なし。
自己ループ・多重辺に対応。最短・辞書順最小は保証しない。
非再帰 DFS を使い、時間・空間ともに O(n + m)。
"""


def find_cycle_directed(n, edges):
    """n 頂点の有向グラフの閉路を (ok, vertices, edge_ids) で返す。O(n+m)。"""
    g = [[] for _ in range(n)]
    for eid, (u, v) in enumerate(edges):
        g[u].append(eid)
    return _find_cycle(g, edges)


def find_cycle_undirected(n, edges):
    """n 頂点の無向グラフの閉路を (ok, vertices, edge_ids) で返す。O(n+m)。

    自己ループは長さ 1、平行な異なる 2 辺は長さ 2 の閉路になる。
    vertices は各辺を実際に通る向きも表す。
    """
    g = [[] for _ in range(n)]
    for eid, (u, v) in enumerate(edges):
        g[u].append(eid)
        g[v].append(eid)
    return _find_cycle(g, edges)


def _find_cycle(g, edges):
    n = len(g)
    state = [0] * n  # 0: 未訪問, 1: DFS 中, 2: 完了
    pos = [-1] * n
    for root in range(n):
        if state[root]:
            continue
        st_v = [root]
        st_e = [-1]  # 各頂点に入った辺番号
        state[root] = 1
        pos[root] = 0
        while st_v:
            v = st_v[-1]
            if not g[v]:
                state[v] = 2
                st_v.pop()
                st_e.pop()
                continue
            eid = g[v].pop()
            if eid == st_e[-1]:  # 無向辺の逆走だけを除外する
                continue
            u, w = edges[eid]
            to = u ^ w ^ v
            if state[to] == 1:
                p = pos[to]
                return True, st_v[p:] + [to], st_e[p + 1:] + [eid]
            if state[to] == 0:
                state[to] = 1
                pos[to] = len(st_v)
                st_v.append(to)
                st_e.append(eid)
    return False, [], []
