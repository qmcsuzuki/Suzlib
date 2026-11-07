# competitive-verifier: STANDALONE
from itertools import product
from random import Random

from python.graph.flow.DAGLowerBoundMinCostFlow import DAGLowerBoundMinCostFlow


def rejects(fn, error=RuntimeError):
    try:
        fn()
    except error:
        return
    raise AssertionError("expected exception")


def check(n, s, t, amount, edges):
    best = None
    for fs in product(*(range(lo, hi + 1) for _, _, lo, hi, _ in edges)):
        balance = [0] * n
        cost = 0
        for (u, v, _, _, c), f in zip(edges, fs):
            balance[u] += f
            balance[v] -= f
            cost += f * c
        target = [0] * n
        target[s], target[t] = amount, -amount
        if balance == target and (best is None or cost < best):
            best = cost
    for dense in (False, True):
        g = DAGLowerBoundMinCostFlow(n, s, t, amount, dense=dense)
        for i, e in enumerate(edges):
            assert g.add_edge(*e) == i
        rejects(g.edges)
        result = g.solve()
        assert result == ((-1, 0) if best is None else (amount, best)), (edges, result, best)
        rejects(g.solve)
        rejects(lambda: g.add_edge(s, t, 0, 1, 0))
        if best is None:
            rejects(g.edges)
            continue
        balance = [0] * n
        cost = 0
        for i, e in enumerate(g.edges()):
            u, v, lo, hi, c = edges[i]
            assert (e.src, e.dst, e.lower, e.upper, e.cost) == (u, v, lo, hi, c)
            assert lo <= e.flow <= hi
            balance[u] += e.flow
            balance[v] -= e.flow
            cost += e.flow * c
        target = [0] * n
        target[s], target[t] = amount, -amount
        assert balance == target and cost == best


rng = Random(1107)
for _ in range(1000):
    n = rng.randrange(2, 6)
    order = list(range(n))
    rng.shuffle(order)
    pairs = [(order[i], order[j]) for i in range(n) for j in range(i + 1, n)]
    edges = []
    for _ in range(rng.randrange(8)):
        u, v = rng.choice(pairs)
        hi = rng.randrange(4)
        edges.append((u, v, rng.randrange(hi + 1), hi, rng.randrange(-5, 6)))
    s, t = rng.sample(range(n), 2)
    check(n, s, t, rng.randrange(4), edges)

check(2, 0, 1, 0, [])
check(2, 0, 1, 1, [])
check(3, 0, 2, 5, [(0, 1, 2, 7, 3), (1, 2, 1, 6, -4)])
check(4, 0, 3, 1, [(0, 3, 0, 1, 0), (1, 2, 1, 1, -10)])
for dense in (False, True):
    g = DAGLowerBoundMinCostFlow(2, 1, 0, 10**18, dense=dense)
    g.add_edge(1, 0, 10**18 - 1, 10**18 + 1, -10**30)
    assert g.solve() == (10**18, -10**48)
    assert g.get_edge(0).flow == 10**18
for edges in [[(0, 0)], [(0, 1), (1, 0)]]:
    g = DAGLowerBoundMinCostFlow(2, 0, 1, 0)
    for u, v in edges:
        g.add_edge(u, v, 0, 0, -1)
    rejects(g.solve, ValueError)
rejects(lambda: DAGLowerBoundMinCostFlow(2, 0, 0, 0), AssertionError)
rejects(lambda: DAGLowerBoundMinCostFlow(2, 0, 1, -1), AssertionError)
g = DAGLowerBoundMinCostFlow(2, 0, 1, 0)
rejects(lambda: g.add_edge(0, 1, 2, 1, 0), AssertionError)
print("DAGLowerBoundMinCostFlow: 2008 brute-force comparisons and regressions passed")
