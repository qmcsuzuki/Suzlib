# competitive-verifier: STANDALONE

from itertools import product
from random import Random

from python.graph.flow.DAGPathCover import DAGPathCover


def brute(n, edges, required, starts, ends, disjoint):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    masks = set()
    stack = [(v, 1 << v) for v in range(n) if starts[v]]
    while stack:
        v, mask = stack.pop()
        if ends[v]:
            masks.add(mask)
        for w in adj[v]:
            stack.append((w, mask | (1 << w)))
    target = sum(1 << v for v in range(n) if required[v])
    dp = [n + 1] * (1 << n)
    dp[0] = 0
    for used in range(1 << n):
        for mask in masks:
            if disjoint and used & mask:
                continue
            nxt = used | mask
            dp[nxt] = min(dp[nxt], dp[used] + 1)
    answer = min(dp[mask] for mask in range(1 << n) if mask & target == target)
    return answer if answer <= n else -1


def rejects(action, error):
    try:
        action()
    except error:
        return
    raise AssertionError("invalid call accepted")


def check(n, edges, required, starts, ends, disjoint):
    g = DAGPathCover(n, disjoint)
    rejects(g.paths, RuntimeError)
    for i, (u, v) in enumerate(edges):
        assert g.add_edge(u, v) == i
    for v in range(n):
        g.set_required(v, required[v])
        g.set_start_allowed(v, starts[v])
        g.set_end_allowed(v, ends[v])
    expected = brute(n, edges, required, starts, ends, disjoint)
    actual = g.solve()
    assert actual == expected, (n, edges, required, starts, ends, disjoint, actual, expected)
    assert g.solve() == actual
    if actual == -1:
        rejects(g.paths, RuntimeError)
        return
    paths = g.paths()
    assert paths == g.paths()
    assert len(paths) == actual
    used = [0] * n
    edge_set = set(edges)
    for path in paths:
        assert path and starts[path[0]] and ends[path[-1]]
        assert len(set(path)) == len(path)
        assert all((u, v) in edge_set for u, v in zip(path, path[1:]))
        for v in path:
            used[v] += 1
    assert all(not required[v] or used[v] for v in range(n))
    assert not disjoint or max(used, default=0) <= 1
    if paths:
        paths[0].clear()
        assert g.paths()[0]


# 3 頂点の全 DAG（固定トポロジカル順）と全設定。
n = 3
possible = [(0, 1), (0, 2), (1, 2)]
for bits in product((False, True), repeat=3):
    edges = [e for e, bit in zip(possible, bits) if bit]
    for flags in product((False, True), repeat=9):
        for disjoint in (False, True):
            check(n, edges, flags[:3], flags[3:6], flags[6:], disjoint)

# 頂点番号を並べ替え、多重辺も含めて大きめの DAG を比較。
rng = Random(20261103)
for _ in range(1500):
    n = rng.randrange(8)
    order = list(range(n))
    rng.shuffle(order)
    edges = [(order[i], order[j]) for i in range(n) for j in range(i + 1, n)
             if rng.randrange(3) == 0]
    if edges and rng.randrange(2):
        edges.append(rng.choice(edges))
    required = [bool(rng.randrange(2)) for _ in range(n)]
    starts = [bool(rng.randrange(2)) for _ in range(n)]
    ends = [bool(rng.randrange(2)) for _ in range(n)]
    for disjoint in (False, True):
        check(n, edges, required, starts, ends, disjoint)
        check(n, edges, required, [True] * n, [True] * n, disjoint)
        check(n, edges, [True] * n, [True] * n, [True] * n, disjoint)

# 設定変更・辺追加による再計算と失敗からの復帰。
g = DAGPathCover(2)
assert g.solve() == 2
g.add_edge(0, 1)
rejects(g.paths, RuntimeError)
assert g.solve() == 1 and g.paths() == [[0, 1]]
g.set_start_allowed(0, False)
rejects(g.paths, RuntimeError)
assert g.solve() == -1
g.set_required(0, False)
assert g.solve() == 1 and g.paths() == [[1]]
g.set_end_allowed(1, False)
assert g.solve() == -1
g.set_required(1, False)
assert g.solve() == 0 and g.paths() == []
g.add_edge(1, 0)
rejects(g.solve, ValueError)  # 必須頂点なしでも DAG 検査を省略しない。
g = DAGPathCover(1)
g.add_edge(0, 0)
rejects(g.solve, ValueError)

# 再帰に依存しない長いパスの復元。3 分岐すべてを通す。
for mode in range(3):
    n = 5000
    g = DAGPathCover(n, mode == 0)
    for v in range(n - 1):
        g.add_edge(v, v + 1)
    if mode == 2:
        g.set_start_allowed(1, False)
    assert g.solve() == 1
    assert g.paths() == [list(range(n))]

print("DAGPathCover: exhaustive, randomized, lifecycle and long-path tests passed")
