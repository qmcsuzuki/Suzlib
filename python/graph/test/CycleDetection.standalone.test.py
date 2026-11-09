# competitive-verifier: STANDALONE

from random import Random
from python.graph.CycleDetection import find_cycle_directed, find_cycle_undirected


def has_cycle(n, edges, directed):
    if directed:
        g = [[] for _ in range(n)]
        deg = [0] * n
        for u, v in edges:
            g[u].append(v)
            deg[v] += 1
        q = [v for v in range(n) if deg[v] == 0]
        for v in q:
            for w in g[v]:
                deg[w] -= 1
                if deg[w] == 0:
                    q.append(w)
        return len(q) != n
    parent = list(range(n))
    def root(v):
        while parent[v] != v:
            v = parent[v]
        return v
    for u, v in edges:
        u, v = root(u), root(v)
        if u == v:
            return True
        parent[u] = v
    return False


def check(n, edges, directed, expected=None):
    original = edges[:]
    fn = find_cycle_directed if directed else find_cycle_undirected
    ok, vs, es = fn(n, edges)
    assert edges == original
    if expected is None:
        expected = has_cycle(n, edges, directed)
    assert ok == expected, (n, edges, directed)
    if not ok:
        assert vs == es == []
        return
    assert es and len(vs) == len(es) + 1 and vs[0] == vs[-1]
    assert len(set(vs[:-1])) == len(es) == len(set(es))
    for a, b, eid in zip(vs, vs[1:], es):
        assert 0 <= eid < len(edges)
        u, v = edges[eid]
        assert (a, b) == (u, v) or (not directed and (a, b) == (v, u))


def main():
    rng = Random(0)
    for directed in (True, False):
        for n, edges in [(0, []), (3, []), (1, [(0, 0)]),
                         (2, [(0, 1)]), (2, [(0, 1), (0, 1)]),
                         (2, [(0, 1), (1, 0)]),
                         (5, [(0, 1), (2, 3), (3, 4), (4, 2)])]:
            check(n, edges, directed)
        for n in range(1, 13):
            for _ in range(500):
                edges = [(rng.randrange(n), rng.randrange(n))
                         for _ in range(rng.randrange(3 * n + 1))]
                check(n, edges, directed)
        n = 200000
        edges = [(v, v + 1) for v in range(n - 1)]
        check(n, edges, directed, False)
        edges.append((n - 1, 0))
        check(n, edges, directed, True)


if __name__ == "__main__":
    main()
