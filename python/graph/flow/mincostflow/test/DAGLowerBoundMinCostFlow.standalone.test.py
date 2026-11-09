# competitive-verifier: STANDALONE
from itertools import product
from random import Random

from python.graph.flow.mincostflow.DAGLowerBoundMinCostFlow import DAGLowerBoundMinCostFlow


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

# 可変流量: 上限あり/なし、流量最大優先/費用最小優先を独立に全探索する。
variable_tests = 0
for _ in range(500):
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
    candidates = []
    for fs in product(*(range(lo, hi + 1) for _, _, lo, hi, _ in edges)):
        balance = [0] * n
        cost = 0
        for (u, v, _, _, c), f in zip(edges, fs):
            balance[u] += f
            balance[v] -= f
            cost += f * c
        amount = balance[s]
        if amount >= 0 and balance[t] == -amount and all(
            balance[v] == 0 for v in range(n) if v != s and v != t
        ):
            candidates.append((amount, cost))
    for limit, method, dense in product((None, 0, 1, 3), ("flow", "min_cost_flow"), (False, True)):
        feasible = [x for x in candidates if limit is None or x[0] <= limit]
        key = (lambda x: (-x[0], x[1])) if method == "flow" else (lambda x: (x[1], x[0]))
        expected = min(feasible, key=key) if feasible else (-1, 0)
        g = DAGLowerBoundMinCostFlow(n, s, t, flow=limit, dense=dense)
        for e in edges:
            g.add_edge(*e)
        result = getattr(g, method)()
        assert result == expected, (edges, s, t, limit, method, result, expected)
        rejects(g.flow)
        rejects(g.min_cost_flow)
        if result[0] == -1:
            rejects(g.edges)
        else:
            balance = [0] * n
            cost = 0
            for e in g.edges():
                assert e.lower <= e.flow <= e.upper
                balance[e.src] += e.flow
                balance[e.dst] -= e.flow
                cost += e.flow * e.cost
            target = [0] * n
            target[s], target[t] = result[0], -result[0]
            assert balance == target and cost == result[1]
        variable_tests += 1

# 正費用でも下限分は必須。同費用なら min_cost_flow は流量最小。
for method, expected in [("solve", (5, 0)), ("flow", (5, 0)), ("min_cost_flow", (2, 0))]:
    g = DAGLowerBoundMinCostFlow(2, 0, 1, flow=5)
    g.add_edge(0, 1, 2, 8, 0)
    assert getattr(g, method)() == expected
for method, expected in [("flow", (8, 24)), ("min_cost_flow", (2, 6))]:
    g = DAGLowerBoundMinCostFlow(2, 0, 1)
    g.add_edge(0, 1, 2, 8, 3)
    assert getattr(g, method)() == expected
g = DAGLowerBoundMinCostFlow(2, 0, 1)
rejects(g.solve, ValueError)
assert g.min_cost_flow() == (0, 0)
for method, expected in [("flow", (10**18, 10**48)), ("min_cost_flow", (1, 10**30))]:
    g = DAGLowerBoundMinCostFlow(2, 0, 1)
    g.add_edge(0, 1, 1, 10**18, 10**30)
    assert getattr(g, method)() == expected
print("Variable flow:", variable_tests, "brute-force comparisons and regressions passed")
