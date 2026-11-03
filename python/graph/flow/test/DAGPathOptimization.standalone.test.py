# competitive-verifier: STANDALONE
from itertools import combinations_with_replacement, product
from random import Random
from python.graph.flow.DAGPathOptimization import DAGPathOptimization


def rejects(fn, error=RuntimeError):
    try:
        fn()
    except error:
        return
    raise AssertionError('expected exception')


def check(n, edges, weights, starts, ends, k, disjoint, once, exact, dense):
    candidates = []
    stack = [([v], [], 0) for v in range(n) if starts[v]]
    while stack:
        vs, es, cost = stack.pop()
        if ends[vs[-1]]:
            candidates.append((vs, es, cost))
        for i, (u, v, c) in enumerate(edges):
            if u == vs[-1]:
                stack.append((vs + [v], es + [i], cost + c))
    best = None
    for count in ([k] if exact else range(k + 1)):
        for chosen in combinations_with_replacement(range(len(candidates)), count):
            used = [0] * n
            cost = 0
            for i in chosen:
                vs, es, c = candidates[i]
                cost += c
                for v in vs:
                    used[v] += 1
            if disjoint and max(used, default=0) > 1:
                continue
            gain = sum(w * (int(x > 0) if once else x) for w, x in zip(weights, used)) - cost
            key = (gain, -count)
            if best is None or key > best:
                best = key
    expected = (-1, 0) if best is None else (-best[1], best[0])
    g = DAGPathOptimization(n, dense=dense)
    for i, e in enumerate(edges):
        assert g.add_edge(*e) == i
    rejects(g.paths)
    actual = g.solve(k, weights, disjoint, once, exact, starts, ends)
    assert actual == expected, (edges, weights, k, disjoint, once, exact, actual, expected)
    if actual[0] == -1:
        rejects(g.paths)
        return
    paths, edge_paths = g.paths(), g.edge_paths()
    assert len(paths) == len(edge_paths) == actual[0]
    used = [0] * n
    cost = 0
    for vs, es in zip(paths, edge_paths):
        assert vs and starts[vs[0]] and ends[vs[-1]]
        assert len(es) + 1 == len(vs) == len(set(vs))
        for u, v, i in zip(vs, vs[1:], es):
            assert edges[i][:2] == (u, v)
            cost += edges[i][2]
        for v in vs:
            used[v] += 1
    assert not disjoint or max(used, default=0) <= 1
    assert sum(w * (int(x > 0) if once else x) for w, x in zip(weights, used)) - cost == actual[1]
    assert paths == g.paths() and edge_paths == g.edge_paths()
    if paths:
        paths[0].clear()
        assert g.paths()[0]


rng = Random(1103)
tests = 0
for _ in range(180):
    n = rng.randrange(6)
    order = list(range(n))
    rng.shuffle(order)
    edges = [(order[i], order[j], rng.randrange(-3, 4))
             for i in range(n) for j in range(i + 1, n) if rng.randrange(3) == 0]
    if edges and rng.randrange(2):
        u, v, _ = rng.choice(edges)
        edges.append((u, v, rng.randrange(-3, 4)))
    starts = [bool(rng.randrange(2)) for _ in range(n)]
    ends = [bool(rng.randrange(2)) for _ in range(n)]
    for disjoint, once, exact, dense in product((False, True), repeat=4):
        weights = [rng.randrange(4) if once and not disjoint else rng.randrange(-3, 4)
                   for _ in range(n)]
        for k in range(4):
            check(n, edges, weights, starts, ends, k, disjoint, once, exact, dense)
            tests += 1

# TDPC R の例1の DAG。報酬共有、同利得なら本数最小。
g = DAGPathOptimization(4)
for u in range(3):
    g.add_edge(u, 3)
assert g.solve(2, [1] * 4) == (2, 3)
assert g.solve(3, [1] * 4) == (3, 4)
assert g.solve(10, [1] * 4) == (3, 4)
assert g.solve(2, [1] * 4, gain_once=False) == (2, 4)
assert g.solve(2) == (0, 0) and g.paths() == []
assert g.solve(2, exact=True) == (2, 0)
assert g.solve(5, vertex_disjoint=True, exact=True) == (-1, 0)
rejects(g.paths)
assert g.solve(1, [1] * 4) == (1, 2)
rejects(lambda: g.solve(1, [-1] * 4), ValueError)
rejects(g.paths)
rejects(lambda: g.solve(1, [1]), AssertionError)
assert g.solve(1, [1] * 4) == (1, 2)
g.add_edge(3, 0)
rejects(g.paths)
rejects(lambda: g.solve(0), ValueError)
g = DAGPathOptimization(1)
g.add_edge(0, 0)
rejects(lambda: g.solve(1), ValueError)

# 大きな整数、同一パスの重複、非再帰の復元、入力配列非保持。
g = DAGPathOptimization(1)
w = [10**30]
assert g.solve(10**6, w, gain_once=False, exact=True) == (10**6, 10**36)
w[0] = 0
assert g.solve(1, [7]) == (1, 7)
assert g.paths() == [[0]]
g = DAGPathOptimization(2500)
for v in range(2499):
    g.add_edge(v + 1, v, -1)
assert g.solve(1) == (1, 2499)
assert g.paths() == [list(range(2499, -1, -1))]
print('DAGPathOptimization:', tests, 'brute-force comparisons and regression tests passed')
