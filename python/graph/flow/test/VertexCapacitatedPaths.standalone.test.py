# competitive-verifier: STANDALONE
from random import Random
from functools import lru_cache

from python.graph.flow.VertexCapacitatedPaths import VertexCapacitatedPaths
from python.graph.flow.MaxFlow import MFGraph


def rejects(fn):
    try:
        fn()
    except RuntimeError:
        return
    raise AssertionError('expected RuntimeError')


def check(n, edges, vc, sc, ec, limit):
    g = VertexCapacitatedPaths(n, vertex_capacity=vc, start_capacity=sc,
                              end_capacity=ec, path_limit=limit)
    adj = [[] for _ in range(n)]
    for i, (u, v, c, undirected) in enumerate(edges):
        add = g.add_undirected_edge if undirected else g.add_edge
        assert add(u, v, c) == i
        adj[u].append((v, i))
        if undirected:
            adj[v].append((u, i))
    candidates = []
    for s in range(n):
        if not sc[s]:
            continue
        stack = [([s], [])]
        while stack:
            vs, es = stack.pop()
            v = vs[-1]
            if ec[v]:
                use = [0] * (3*n+len(edges))
                for w in vs:
                    use[w] += 1
                use[n+s] = use[2*n+v] = 1
                for e in es:
                    use[3*n+e] += 1
                candidates.append(tuple(use))
            for w, e in adj[v]:
                if w not in vs:
                    stack.append((vs+[w], es+[e]))
    capacity = tuple(vc+sc+ec+[c for _, _, c, _ in edges])

    @lru_cache(None)
    def brute(remaining, k):
        if not k:
            return 0
        best = 0
        for use in candidates:
            if all(a >= b for a, b in zip(remaining, use)):
                best = max(best, 1+brute(tuple(a-b for a, b in zip(remaining, use)), k-1))
        return best

    expected = brute(capacity, min(sum(sc), sum(ec)) if limit is None else limit)
    rejects(g.paths)
    assert g.solve() == expected, (edges, vc, sc, ec, limit, expected)
    rejects(g.solve)
    if n:
        rejects(lambda: g.add_edge(0, 0))
    paths, epaths = g.paths(), g.edge_paths()
    assert len(paths) == len(epaths) == expected
    use = [0] * len(capacity)
    direction = [0] * len(edges)
    for vs, es in zip(paths, epaths):
        assert len(vs) == len(es)+1 and len(vs) == len(set(vs))
        use[n+vs[0]] += 1
        use[2*n+vs[-1]] += 1
        for v in vs:
            use[v] += 1
        for u, v, i in zip(vs, vs[1:], es):
            a, b, _, undirected = edges[i]
            sign = 1 if (u, v) == (a, b) else -1
            assert sign == 1 or undirected and (u, v) == (b, a)
            if undirected:
                assert direction[i] in (0, sign)
                direction[i] = sign
            use[3*n+i] += 1
    assert all(a <= b for a, b in zip(use, capacity))
    assert g.paths() == paths and g.edge_paths() == epaths
    if paths:
        paths[0].clear()
        assert g.paths()[0]


rng = Random(724)
for _ in range(250):
    n = rng.randrange(1, 5)
    edges = [(rng.randrange(n), rng.randrange(n), rng.randrange(3), bool(rng.randrange(2)))
             for _ in range(rng.randrange(7))]
    vc = [rng.randrange(3) for _ in range(n)]
    sc, ec = [0]*n, [0]*n
    for _ in range(3):
        sc[rng.randrange(n)] += 1
        ec[rng.randrange(n)] += 1
    check(n, edges, vc, sc, ec, rng.choice([None, 0, 1, 2, 3]))
check(0, [], [], [], [], None)

# 点素、直通辺、多重辺、容量0、到達不能、無制限。
for limit in (None, 0, 1, 2, 10):
    g = VertexCapacitatedPaths.st(4, 0, 3, path_limit=limit)
    for u, v in [(0, 1), (1, 3), (0, 2), (2, 3), (0, 3), (0, 3)]:
        g.add_undirected_edge(u, v)
    assert g.solve() == (4 if limit is None else min(4, limit))
    assert all(p[0] == 0 and p[-1] == 3 for p in g.paths())
g = VertexCapacitatedPaths.st(2, 0, 1)
assert g.solve() == 0 and g.paths() == []

# 巨大な重複パスは復元を要求するまで展開しない。
g = VertexCapacitatedPaths.st(2, 0, 1)
g.add_edge(0, 1, 10**12)
assert g.solve() == 10**12 and not g._parts

# 逆向き流を含む実行可能フローを注入し、明示的な相殺を検証。
original_flow = MFGraph.flow

def with_cycle(self, s, t, flow_limit=None):
    result = original_flow(self, s, t, flow_limit)
    # 頂点辺 0,1 と無向辺の両方向 4,5 に循環を加える。
    for i in (0, 1, 4, 5):
        e = self.get_edge(i)
        self.change_edge(i, e.cap, e.flow+1)
    return result

MFGraph.flow = with_cycle
try:
    g = VertexCapacitatedPaths(2, vertex_capacity=[3, 3],
                              start_capacity=[1, 0], end_capacity=[0, 1])
    g.add_undirected_edge(0, 1, 3)
    assert g.solve() == 1
    assert g._graph.get_edge(4).flow == 1
    assert g._graph.get_edge(5).flow == 0
    assert g.paths() == [[0, 1]] and g.edge_paths() == [[0]]
finally:
    MFGraph.flow = original_flow
print('VertexCapacitatedPaths: OK (250 random exhaustive comparisons)')
