# competitive-verifier: STANDALONE
from itertools import combinations_with_replacement, product
from random import Random
from python.graph.flow.DAGPathCover import DAGPathCover


def rejects(fn, error=RuntimeError):
    try:
        fn()
    except error:
        return
    raise AssertionError('expected exception')


def check(n, edges, required, weights, starts, ends, bc, ec, k, disjoint, once, exact, dense):
    candidates = []
    stack = [([v], bc[v]) for v in range(n) if starts[v]]
    while stack:
        vs, cost = stack.pop()
        if ends[vs[-1]]:
            candidates.append((vs, cost + ec[vs[-1]]))
        for u, v, c in edges:
            if u == vs[-1]:
                stack.append((vs + [v], cost + c))
    best = None
    for count in ([k] if exact else range(k + 1)):
        for chosen in combinations_with_replacement(range(len(candidates)), count):
            used = [0] * n
            start_count = [0] * n
            end_count = [0] * n
            cost = 0
            for i in chosen:
                vs, c = candidates[i]
                start_count[vs[0]] += 1
                end_count[vs[-1]] += 1
                cost += c
                for v in vs:
                    used[v] += 1
            if any(x > cap for x, cap in zip(start_count, starts)):
                continue
            if any(x > cap for x, cap in zip(end_count, ends)):
                continue
            if disjoint and max(used, default=0) > 1:
                continue
            if any(r and not x for r, x in zip(required, used)):
                continue
            cost -= sum(w * (int(x > 0) if once else x) for w, x in zip(weights, used))
            key = (cost, count)
            if best is None or key < best:
                best = key
    expected = (-1, 0) if best is None else (best[1], best[0])
    kw = dict(path_count=k if exact else None, path_limit=None if exact else k)
    g = DAGPathCover(n, vertex_disjoint=disjoint, required=required,
                     vertex_gain=weights, gain_once=once, start_cost=bc, end_cost=ec,
                     start_capacity=starts, end_capacity=ends, dense=dense, **kw)
    for i, e in enumerate(edges):
        assert g.add_edge(*e) == i
    rejects(g.paths)
    actual = g.solve()
    assert actual == expected, (edges, required, weights, bc, ec, k, disjoint, once, exact, actual, expected)
    rejects(g.solve)
    if n:
        rejects(lambda: g.add_edge(0, 0))
    if actual[0] == -1:
        rejects(g.paths)
        rejects(g.edge_paths)
        return
    paths, edge_paths = g.paths(), g.edge_paths()
    assert len(paths) == len(edge_paths) == actual[0]
    used = [0] * n
    start_count = [0] * n
    end_count = [0] * n
    cost = 0
    for vs, es in zip(paths, edge_paths):
        assert vs and starts[vs[0]] and ends[vs[-1]]
        start_count[vs[0]] += 1
        end_count[vs[-1]] += 1
        cost += bc[vs[0]] + ec[vs[-1]]
        assert len(es) + 1 == len(vs) == len(set(vs))
        for u, v, i in zip(vs, vs[1:], es):
            assert edges[i][:2] == (u, v)
            cost += edges[i][2]
        for v in vs:
            used[v] += 1
    assert all(x <= cap for x, cap in zip(start_count, starts))
    assert all(x <= cap for x, cap in zip(end_count, ends))
    assert not disjoint or max(used, default=0) <= 1
    assert all(not r or x for r, x in zip(required, used))
    cost -= sum(w * (int(x > 0) if once else x) for w, x in zip(weights, used))
    assert cost == actual[1]
    assert paths == g.paths() and edge_paths == g.edge_paths()
    if paths:
        paths[0].clear()
        assert g.paths()[0]


rng = Random(1104)
tests = 0
for _ in range(200):
    n = rng.randrange(6)
    order = list(range(n))
    rng.shuffle(order)
    edges = [(order[i], order[j], rng.randrange(-3, 4))
             for i in range(n) for j in range(i + 1, n) if rng.randrange(3) == 0]
    if edges and rng.randrange(2):
        u, v, _ = rng.choice(edges)
        edges.append((u, v, rng.randrange(-3, 4)))
    starts = [rng.randrange(4) for _ in range(n)]
    ends = [rng.randrange(4) for _ in range(n)]
    required = [bool(rng.randrange(2)) for _ in range(n)]
    bc = [rng.randrange(-3, 4) for _ in range(n)]
    ec = [rng.randrange(-3, 4) for _ in range(n)]
    for disjoint, once, exact, dense in product((False, True), repeat=4):
        weights = [rng.randrange(4) if once and not disjoint else rng.randrange(-3, 4)
                   for _ in range(n)]
        for k in range(4):
            check(n, edges, required, weights, starts, ends, bc, ec, k, disjoint, once, exact, dense)
            tests += 1

# 特殊帰着を確実に通す。必須なし (点素・共有) / 点素全被覆。
# 本数固定・本数上限、負費用、多重辺、復元を全探索と比較する。
for _ in range(50):
    n = rng.randrange(1, 6)
    order = list(range(n))
    rng.shuffle(order)
    edges = [(order[i], order[j], rng.randrange(-4, 5))
             for i in range(n) for j in range(i + 1, n)
             if rng.randrange(2) == 0]
    if edges:
        u, v, _ = rng.choice(edges)
        edges.append((u, v, rng.randrange(-4, 5)))
    bc = [rng.randrange(-4, 5) for _ in range(n)]
    ec = [rng.randrange(-4, 5) for _ in range(n)]
    for required, disjoint in [([False]*n, True), ([False]*n, False),
                               ([True]*n, True)]:
        for once, exact, dense in product((False, True), repeat=3):
            weights = [rng.randrange(5) if once and not disjoint
                       else rng.randrange(-4, 5) for _ in range(n)]
            for k in range(min(n + 1, 4)):
                check(n, edges, required, weights, [k]*n, [k]*n,
                      bc, ec, k, disjoint, once, exact, dense)
                tests += 1

# 全被覆は「初期単頂点パスからの結合」。同費用なら結合数最大。
g = DAGPathCover(4, path_limit=4, start_cost=0,
                 vertex_disjoint=True, required=True, path_count=None, end_cost=0, vertex_gain=0, gain_once=True)
for u, v in [(0, 1), (1, 2), (2, 3)]:
    g.add_edge(u, v)
assert g.solve() == (1, 0)
assert g.paths() == [[0, 1, 2, 3]]

# 全被覆・本数上限の不可能判定。マッチング数が n-K に届かない。
g = DAGPathCover(4, path_limit=1,
                 vertex_disjoint=True, required=True, path_count=None, start_cost=1, end_cost=0, vertex_gain=0, gain_once=True)
g.add_edge(0, 1)
assert g.solve() == (-1, 0)
rejects(g.paths)

# 始終点制限がある全被覆は一般帰着へフォールバック。
g = DAGPathCover(3, path_count=1, start_capacity=[1, 0, 0],
                 end_capacity=[0, 0, 1],
                 vertex_disjoint=True, required=True, path_limit=None, start_cost=1, end_cost=0, vertex_gain=0, gain_once=True)
g.add_edge(0, 1)
g.add_edge(1, 2)
assert g.solve() == (1, 1)
assert g.paths() == [[0, 1, 2]]

# PAST202107 M の3例。費用変換なしで全頂点被覆。
for a, c, expected in [([4,25,1000000000,9,19,22],10,44),
                        ([3,1,4,1,5],100,112),
                        ([6708,1391,3108,7953,7797,2370,7699,1098,2362,2359],5301,17095)]:
    for dense in (False, True):
        g = DAGPathCover(len(a), start_cost=c, dense=dense,
                         vertex_disjoint=True, required=True, path_count=None, path_limit=None, end_cost=0, vertex_gain=0, gain_once=True)
        for j in range(len(a)):
            for i in range(j):
                g.add_edge(i, j, abs(a[i]-a[j]))
        assert g.solve()[1] == expected
        assert sorted(v for p in g.paths() for v in p) == list(range(len(a)))

# TDPC R の例1、および例2のSCC縮約後（成分 {2,5} の重み2）。
for n, edges, weights, expected in [
    (4, [(0,3),(1,3),(2,3)], [1]*4, 3),
    (5, [(0,2),(1,2),(2,3),(2,4)], [1,1,2,1,1], 6),
]:
    g = DAGPathCover(n, vertex_disjoint=False, required=False, path_limit=2,
                     start_cost=0, vertex_gain=weights,
                     path_count=None, end_cost=0, gain_once=True)
    for e in edges:
        g.add_edge(*e)
    assert g.solve()[1] == -expected

# 通常のパス被覆、共有による改善、同費用なら本数最小。
for disjoint, expected in [(True,3),(False,2)]:
    g = DAGPathCover(5, vertex_disjoint=disjoint,
                     required=True, path_count=None, path_limit=None, start_cost=1, end_cost=0, vertex_gain=0, gain_once=True)
    for e in [(0,2),(1,2),(2,3),(2,4)]:
        g.add_edge(*e)
    assert g.solve() == (expected, expected)
for required, expected in [(True,(1,0)), (False,(0,0))]:
    g = DAGPathCover(3, required=required, start_cost=0,
                     vertex_disjoint=True, path_count=None, path_limit=None, end_cost=0, vertex_gain=0, gain_once=True)
    g.add_edge(0,1)
    g.add_edge(1,2)
    assert g.solve() == expected

# 入力配列のコピー、空グラフ、失敗時の復元禁止、引数の検査。
r = [True]
b = [5]
g = DAGPathCover(1, required=r, start_cost=b,
                 vertex_disjoint=True, path_count=None, path_limit=None, end_cost=0, vertex_gain=0, gain_once=True)
r[0], b[0] = False, -100
assert g.solve() == (1,5)
assert DAGPathCover(0,
                    vertex_disjoint=True, required=True, path_count=None, path_limit=None, start_cost=1, end_cost=0, vertex_gain=0, gain_once=True).solve() == (0,0)
assert DAGPathCover(0, path_count=1,
                    vertex_disjoint=True, required=True, path_limit=None, start_cost=1, end_cost=0, vertex_gain=0, gain_once=True).solve() == (-1,0)
assert DAGPathCover(1, path_limit=0,
                    vertex_disjoint=True, required=True, path_count=None, start_cost=1, end_cost=0, vertex_gain=0, gain_once=True).solve() == (-1,0)
g = DAGPathCover(1, start_capacity=[0],
                 vertex_disjoint=True, required=True, path_count=None, path_limit=None, start_cost=1, end_cost=0, vertex_gain=0, gain_once=True)
assert g.solve() == (-1,0)
rejects(g.paths)
rejects(lambda: DAGPathCover(1, path_count=1, path_limit=2,
                             vertex_disjoint=True, required=True, start_cost=1, end_cost=0, vertex_gain=0, gain_once=True), ValueError)
rejects(lambda: DAGPathCover(2, required=[True],
                             vertex_disjoint=True, path_count=None, path_limit=None, start_cost=1, end_cost=0, vertex_gain=0, gain_once=True), AssertionError)
rejects(lambda: DAGPathCover(1, vertex_disjoint=False, vertex_gain=-1,
                             required=True, path_count=None, path_limit=None, start_cost=1, end_cost=0, gain_once=True), ValueError)
for options in [dict(start_cost=-1),dict(end_cost=-1),dict(gain_once=False)]:
    g = DAGPathCover(1, vertex_disjoint=False, start_cost=options.get("start_cost", 1), end_cost=options.get("end_cost", 0), gain_once=options.get("gain_once", True),
                     required=True, path_count=None, path_limit=None, vertex_gain=0)
    rejects(g.solve, ValueError)
g = DAGPathCover(2, vertex_disjoint=False,
                 required=True, path_count=None, path_limit=None, start_cost=1, end_cost=0, vertex_gain=0, gain_once=True)
g.add_edge(0,1,-1)
rejects(g.solve, ValueError)
for edges in [[(0,0)], [(0,1),(1,0)]]:
    g = DAGPathCover(2, required=False, path_limit=0,
                     vertex_disjoint=True, path_count=None, start_cost=1, end_cost=0, vertex_gain=0, gain_once=True)
    for e in edges:
        g.add_edge(*e)
    rejects(g.solve, ValueError)
    rejects(g.paths)

# 大きな整数と負の最適費用の復号。巨大な流量は一度に流せる。
g = DAGPathCover(1, vertex_disjoint=False, path_count=10**6,
                 start_cost=-10**30, gain_once=False, vertex_gain=7,
                 required=True, path_limit=None, end_cost=0)
assert g.solve() == (10**6, -(10**30+7)*10**6)
# 非再帰復元は必須頂点を端点に限定して長さを検査。
n = 2500
r = [False]*n
r[0] = r[-1] = True
g = DAGPathCover(n, required=r,
                 vertex_disjoint=True, path_count=None, path_limit=None, start_cost=1, end_cost=0, vertex_gain=0, gain_once=True)
for v in range(n-1):
    g.add_edge(v+1,v)
assert g.solve() == (1,1)
assert g.paths() == [list(range(n-1,-1,-1))]
print('DAGPathCover:', tests, 'brute-force comparisons and regressions passed')

# 開始・終了上限は途中の共有とは独立。両方の指定形式と配列コピーも検査する。
for dense, required in product((False, True), repeat=2):
    def make(start_capacity, end_capacity, count=2):
        return DAGPathCover(
            3, vertex_disjoint=False, required=required,
            path_count=count, path_limit=None, start_cost=0, end_cost=0,
            vertex_gain=[1, 1, 1], gain_once=True,
            start_capacity=start_capacity, end_capacity=end_capacity, dense=dense,
        )

    starts = [1, 1, 0]
    g = make(starts, [0, 0, 2])
    starts[0] = 0
    g.add_edge(0, 2)
    g.add_edge(1, 2)
    assert g.solve() == (2, -3)
    assert sorted(g.paths()) == [[0, 2], [1, 2]]
    g = make([1, 1, 0], [0, 0, 1])
    g.add_edge(0, 2)
    g.add_edge(1, 2)
    assert g.solve() == (-1, 0)

    ends = [0, 1, 1]
    g = make([2, 0, 0], ends)
    ends[1] = 0
    g.add_edge(0, 1)
    g.add_edge(0, 2)
    assert g.solve() == (2, -3)
    assert sorted(g.paths()) == [[0, 1], [0, 2]]
    g = make([1, 0, 0], [0, 1, 1])
    g.add_edge(0, 1)
    g.add_edge(0, 2)
    assert g.solve() == (-1, 0)
    assert make(1, 1, count=3).solve() == (3, -3)
    assert make(0, None).solve() == (-1, 0)
    assert make(None, 0).solve() == (-1, 0)
    rejects(lambda: make(-1, None), AssertionError)
    rejects(lambda: make(None, [0, -1, 1]), AssertionError)
    rejects(lambda: make([1], None), AssertionError)
print("Endpoint capacity regressions passed")
