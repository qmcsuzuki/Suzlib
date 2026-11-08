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


def check(n, edges, disjoint=True, required=None, starts=None, ends=None):
    req = [True] * n if required is None else required
    sc = [n] * n if starts is None else starts
    ec = [n] * n if ends is None else ends
    candidates = []
    stack = [[v] for v in range(n) if sc[v]]
    while stack:
        path = stack.pop()
        if ec[path[-1]]:
            candidates.append(path)
        for u, v in set(edges):
            if u == path[-1]:
                stack.append(path + [v])

    def valid(paths):
        used, begin, end = [0] * n, [0] * n, [0] * n
        for path in paths:
            begin[path[0]] += 1
            end[path[-1]] += 1
            for v in path:
                used[v] += 1
        return (all(not r or used[v] for v, r in enumerate(req))
                and (not disjoint or all(x <= 1 for x in used))
                and all(x <= c for x, c in zip(begin, sc))
                and all(x <= c for x, c in zip(end, ec)))

    expected = -1
    # 同じパスの重複は最小解では不要。
    for k in range(sum(req) + 1):
        if any(valid(paths) for paths in combinations(candidates, k)):
            expected = k
            break
    g = DAGMinimumPathCover(n, disjoint, required=required,
                            start_capacity=starts, end_capacity=ends)
    for i, (u, v) in enumerate(edges):
        assert g.add_edge(u, v) == i
    rejects(g.paths)
    rejects(g.edge_paths)
    result = g.solve()
    assert result == expected, (n, edges, disjoint, req, sc, ec, result, expected)
    rejects(g.solve)
    if n:
        rejects(lambda: g.add_edge(0, 0))
    if result < 0:
        rejects(g.paths)
        return
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
for disjoint in (False, True):
    check(5, x, disjoint)
    check(5, x, disjoint, starts=[1, 1, 0, 0, 0], ends=[0, 0, 0, 1, 1])
check(3, [(2, 0), (2, 0), (0, 1)])
check(3, [(2, 0), (0, 1)], False, [False, True, False], [0, 0, 1], [0, 1, 0])
check(2, [(0, 1)], starts=[0, 0])
check(2, [(0, 1)], required=[False, False], starts=[0, 0])
for edges in ([(0, 0)], [(0, 1), (1, 0)]):
    g = DAGMinimumPathCover(2, required=[False, False])
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
    check(n, edges, bool(rng.randrange(2)),
          None if rng.randrange(3) == 0 else [bool(rng.randrange(2)) for _ in range(n)],
          None if rng.randrange(3) == 0 else [rng.randrange(3) for _ in range(n)],
          None if rng.randrange(3) == 0 else [rng.randrange(3) for _ in range(n)])

# 非再帰の復元と基本形の大きめの入力。
n = 5000
g = DAGMinimumPathCover(n)
for v in range(n - 1):
    g.add_edge(v, v + 1)
assert g.solve() == 1
assert g.paths() == [list(range(n))]
print('DAGMinimumPathCover tests passed')
