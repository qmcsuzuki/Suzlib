# competitive-verifier: STANDALONE
from functools import lru_cache
from itertools import combinations
from random import Random

from python.graph.flow.maxflow.DAGMinimumPathCover import DAGMaximumAntichain, DAGMinimumPathCover


def rejects(fn, error=RuntimeError):
    try:
        fn()
    except error:
        return
    raise AssertionError('expected exception')


def check(n, edges):
    candidates = []
    stack = [[v] for v in range(n) ]
    while stack:
        path = stack.pop()
        candidates.append(path)
        for u, v in set(edges):
            if u == path[-1]:
                stack.append(path + [v])

    def valid(paths):
        used = [0] * n
        for path in paths:
            for v in path:
                used[v] += 1
        return used == [1] * n

    expected = -1
    # 同じパスの重複は最小解では不要。
    for k in range(n + 1):
        if any(valid(paths) for paths in combinations(candidates, k)):
            expected = k
            break
    g = DAGMinimumPathCover(n)
    for i, (u, v) in enumerate(edges):
        assert g.add_edge(u, v) == i
    rejects(g.paths)
    rejects(g.edge_paths)
    result = g.solve()
    assert result == expected, (n, edges, result, expected)
    rejects(g.solve)
    if n:
        rejects(lambda: g.add_edge(0, 0))
    paths, edge_paths = g.paths(), g.edge_paths()
    assert len(paths) == len(edge_paths) == result
    assert valid(paths)
    for path, ids in zip(paths, edge_paths):
        assert path and len(ids) == len(path) - 1
        assert [edges[i] for i in ids] == list(zip(path, path[1:]))
    assert g.paths() == paths and g.edge_paths() == edge_paths
    if paths:
        paths[0].clear()
        assert g.paths()[0]


def check_weighted(n, edges, weights, disjoint):
    """weights 付き被覆の本数・復元と、同じ weights の最大重み反鎖を全探索と比較する。"""
    candidates = []
    stack = [[v] for v in range(n)]
    while stack:
        path = stack.pop()
        candidates.append(path)
        for u, v in set(edges):
            if u == path[-1]:
                stack.append(path + [v])

    @lru_cache(None)
    def brute(need, used):
        # need[v]: 残りの必要被覆回数、used: 点素の場合に使用済みの頂点集合
        if not any(need):
            return 0
        best = n * 3
        for path in candidates:
            if disjoint and any(used >> v & 1 for v in path):
                continue
            if all(need[v] == 0 for v in path):
                continue
            rest = list(need)
            mask = used
            for v in path:
                rest[v] = max(0, rest[v] - 1)
                mask |= 1 << v
            best = min(best, 1 + brute(tuple(rest), mask))
        return best

    g = DAGMinimumPathCover(n, disjoint=disjoint, weights=weights)
    for u, v in edges:
        g.add_edge(u, v)
    result = g.solve()
    assert result == brute(tuple(weights), 0), (n, edges, weights, disjoint, result)
    paths, edge_paths = g.paths(), g.edge_paths()
    assert len(paths) == len(edge_paths) == result
    used = [0] * n
    for path, ids in zip(paths, edge_paths):
        assert [edges[i] for i in ids] == list(zip(path, path[1:]))
        for v in path:
            used[v] += 1
    assert all(c >= w for c, w in zip(used, weights))
    if disjoint:
        assert all(c <= 1 for c in used)
        return

    reach = [[False] * n for _ in range(n)]
    for path in candidates:
        for a, b in combinations(path, 2):
            reach[a][b] = True
    comparable = lambda S: any(reach[a][b] or reach[b][a] for a, b in combinations(S, 2))
    expected = max(sum(weights[v] for v in S) for k in range(n + 1)
                   for S in combinations(range(n), k) if not comparable(S))
    g = DAGMaximumAntichain(n, weights)
    for u, v in edges:
        g.add_edge(u, v)
    assert g.solve() == expected == result
    antichain = g.antichain()
    assert not comparable(antichain)
    assert sum(weights[v] for v in antichain) == expected


check(0, [])
check(1, [])
# X 字型。点素では3本、共有可では2本。
x = [(0, 2), (1, 2), (2, 3), (2, 4)]
check(5, x)
g = DAGMaximumAntichain(5)
for e in x:
    g.add_edge(*e)
assert g.solve() == 2
assert g.antichain() in ([0, 1], [3, 4])
paths = g.paths()
assert len(paths) == 2
assert {v for path in paths for v in path} == set(range(5))
assert all(e in x for path in paths for e in zip(path, path[1:]))
assert g.antichain() in ([0, 1], [3, 4])
# 重みはパス被覆自身で扱う。共有可なら各頂点の必要被覆回数を指定できる。
g = DAGMinimumPathCover(5, disjoint=False, weights=[2, 1, 0, 2, 1])
for e in x:
    g.add_edge(*e)
assert g.solve() == 3
paths = g.paths()
assert all(sum(v in path for path in paths) >= w
           for v, w in enumerate([2, 1, 0, 2, 1]))
assert len(g.edge_paths()) == 3

# 点素では必須/任意の指定が可能だが、同じ頂点を2回以上要求できない。
g = DAGMinimumPathCover(3, disjoint=True, weights=[0, 1, 0])
g.add_edge(0, 1)
g.add_edge(1, 2)
assert g.solve() == 1
assert sum(1 in path for path in g.paths()) == 1
g = DAGMinimumPathCover(2, weights=[0, 0])
assert g.solve() == 0 and g.paths() == []
rejects(lambda: DAGMinimumPathCover(2, weights=[2, 0]), ValueError)

# Antichain 側は親クラスへ weights をそのまま渡す。
g = DAGMaximumAntichain(5, weights=[2, 1, 0, 2, 1])
for e in x:
    g.add_edge(*e)
assert g.solve() == 3
assert g.antichain() in ([0, 1], [3, 4])

check(3, [(2, 0), (2, 0), (0, 1)])
check(4, [])
for edges in ([(0, 0)], [(0, 1), (1, 0)]):
    g = DAGMinimumPathCover(2)
    for e in edges:
        g.add_edge(*e)
    rejects(g.solve, ValueError)
    rejects(g.paths)

rng = Random(71)
for _ in range(400):
    n = rng.randrange(1, 6)
    order = list(range(n))
    rng.shuffle(order)
    edges = [(order[u], order[v]) for u in range(n) for v in range(u + 1, n)
             if rng.randrange(3) == 0]
    if edges and rng.randrange(3) == 0:
        edges.append(edges[0])
    check(n, edges)

# weights 付き。点素は 0/1、共有可は 0..2 で、共有可では反鎖とも比較する。
for _ in range(1500):
    n = rng.randrange(0, 6)
    order = list(range(n))
    rng.shuffle(order)
    edges = [(order[u], order[v]) for u in range(n) for v in range(u + 1, n)
             if rng.randrange(3) == 0]
    if edges and rng.randrange(3) == 0:
        edges.append(edges[0])
    disjoint = rng.randrange(2) == 0
    weights = [rng.randrange(2 if disjoint else 3) for _ in range(n)]
    check_weighted(n, edges, weights, disjoint)

# 非再帰の復元と基本形の大きめの入力。
n = 5000
g = DAGMinimumPathCover(n)
for v in range(n - 1):
    g.add_edge(v, v + 1)
assert g.solve() == 1
assert g.paths() == [list(range(n))]
print('DAGMinimumPathCover tests passed')
