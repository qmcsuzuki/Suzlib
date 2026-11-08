# competitive-verifier: STANDALONE
from itertools import combinations
from random import Random

from python.graph.flow.DAGMinimumPathCover import DAGMinimumPathCover


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


check(0, [])
check(1, [])
# X 字型。点素では3本、共有可では2本。
x = [(0, 2), (1, 2), (2, 3), (2, 4)]
check(5, x)
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

# 非再帰の復元と基本形の大きめの入力。
n = 5000
g = DAGMinimumPathCover(n)
for v in range(n - 1):
    g.add_edge(v, v + 1)
assert g.solve() == 1
assert g.paths() == [list(range(n))]
print('DAGMinimumPathCover tests passed')
