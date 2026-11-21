# competitive-verifier: STANDALONE

from itertools import product
from random import Random

from python.graph.flow.mincostflow.MinCostBFlow import MinCostBFlow


def rejects(action):
    try:
        action()
    except AssertionError:
        return
    raise AssertionError('invalid call accepted')


def dag_allowed(n, edges):
    """dag=True で解けるか。正容量の負費用辺がなければ閉路があってもよい。"""
    active = [(u, v) for u, v, lo, hi, _ in edges if lo < hi]
    if not any(lo < hi and c < 0 for _, _, lo, hi, c in edges):
        return True
    indegree = [0] * n
    for _, v in active:
        indegree[v] += 1
    order = [v for v in range(n) if indegree[v] == 0]
    for u in order:
        for a, b in active:
            if a == u:
                indegree[b] -= 1
                if indegree[b] == 0:
                    order.append(b)
    return len(order) == n


def check(n, edges, balance, expected):
    modes = [(dense, False) for dense in (False, True)]
    if dag_allowed(n, edges):
        modes += [(dense, True) for dense in (False, True)]
    for dense, dag in modes:
        g = MinCostBFlow(n, dense=dense, dag=dag)
        for i, e in enumerate(edges):
            assert g.add_edge(*e) == i
        for v, b in enumerate(balance):
            g.add_balance(v, b + 1)
            g.add_balance(v, -1)
        rejects(g.edges)
        rejects(g.potential)
        feasible, cost = g.solve()
        assert feasible == (expected is not None)
        assert cost == (0 if expected is None else expected)
        rejects(g.solve)
        rejects(lambda: g.add_balance(0, 0))
        rejects(lambda: g.add_edge(0, 0, 0, 0, 0))
        if not feasible:
            rejects(g.edges)
            rejects(g.potential)
            continue
        result = g.edges()
        assert len(result) == len(edges)
        actual = [0] * n
        total = 0
        for i, ((u, v, lo, hi, c), e) in enumerate(zip(edges, result)):
            assert e == g.get_edge(i)
            assert (e.src, e.dst, e.lower, e.upper, e.cost) == (u, v, lo, hi, c)
            assert lo <= e.flow <= hi
            actual[u] += e.flow
            actual[v] -= e.flow
            total += e.flow * c
        assert actual == list(balance)
        assert total == cost
        # 最適性の証明書: 増やせる辺は縮約コスト >= 0、減らせる辺は <= 0。
        p = g.potential()
        assert len(p) == n
        for e in result:
            reduced = e.cost + p[e.src] - p[e.dst]
            if e.flow < e.upper:
                assert reduced >= 0
            if e.flow > e.lower:
                assert reduced <= 0
        if dag:
            # 負費用辺も反転していない。
            for i, (u, v, _, _, _) in enumerate(edges):
                assert g._graph.get_edge(i)[:2] == (u, v)


rng = Random(81126)
for _ in range(1000):
    n = rng.randrange(1, 5)
    edges = []
    for _ in range(rng.randrange(8)):
        lo = rng.randrange(3)
        edges.append((rng.randrange(n), rng.randrange(n), lo,
                      lo + rng.randrange(3), rng.randrange(-5, 6)))
    best = {}
    for flows in product(*(range(e[2], e[3] + 1) for e in edges)):
        balance = [0] * n
        cost = 0
        for (u, v, lo, hi, c), f in zip(edges, flows):
            balance[u] += f
            balance[v] -= f
            cost += f * c
        key = tuple(balance)
        if key not in best or cost < best[key]:
            best[key] = cost
    if rng.randrange(2):
        balance = rng.choice(list(best))
    else:
        balance = [rng.randrange(-5, 6) for _ in range(n)]
        if rng.randrange(2):
            balance[-1] -= sum(balance)
    check(n, edges, balance, best.get(tuple(balance)))

# 番号順の DAG、番号をシャッフルした DAG で dag=True も総当たりと比較する。
rng = Random(20261119)
for _ in range(1000):
    n = rng.randrange(1, 6)
    perm = list(range(n))
    if rng.randrange(2):
        rng.shuffle(perm)
    edges = []
    for _ in range(rng.randrange(8) if n >= 2 else 0):
        a, b = sorted(rng.sample(range(n), 2))
        lo = rng.randrange(3)
        edges.append((perm[a], perm[b], lo, lo + rng.randrange(3),
                      rng.randrange(-5, 6)))
    best = {}
    for flows in product(*(range(e[2], e[3] + 1) for e in edges)):
        balance = [0] * n
        cost = 0
        for (u, v, lo, hi, c), f in zip(edges, flows):
            balance[u] += f
            balance[v] -= f
            cost += f * c
        key = tuple(balance)
        if key not in best or cost < best[key]:
            best[key] = cost
    balance = rng.choice(list(best))
    assert dag_allowed(n, edges)
    check(n, edges, balance, best[balance])

# dag=True では、正容量の負費用辺があるとき閉路を拒否する。
g = MinCostBFlow(2, dag=True)
g.add_edge(0, 1, 0, 1, -1)
g.add_edge(1, 0, 0, 1, 0)
rejects(g.solve)
g = MinCostBFlow(1, dag=True)
g.add_edge(0, 0, 0, 1, -1)
rejects(g.solve)
# 負費用辺の容量が巨大でも、dag=True では下限分しか補助辺に流さない。
g = MinCostBFlow(3, dag=True)
g.add_balance(0, 1)
g.add_balance(2, -1)
g.add_edge(0, 1, 0, 10**18, -5)
g.add_edge(1, 2, 0, 10**18, -5)
assert g.solve() == (True, -10)
assert sum(e.cap for e in g._graph.edges()[2:]) == 2

# 空グラフ、需給不一致、総需給0でも実行不能。
check(0, [], [], 0)
check(1, [], [1], None)
check(2, [], [1, -1], None)
# 元の需給0の負閉路。需給のある成分と切り離された負閉路も最適化する。
check(2, [(0, 1, 0, 10, -1), (1, 0, 0, 10, 0)], [0, 0], -10)
check(4, [(0, 1, 0, 3, 2), (2, 3, 0, 10, -1),
          (3, 2, 0, 10, 0)], [3, -3, 0, 0], -4)
# 自己ループ、固定辺、ゼロ容量、巨大容量・費用、最小費用が -1。
check(1, [(0, 0, 2, 10**30, -3), (0, 0, 7, 12, 5),
          (0, 0, 4, 4, -2), (0, 0, 0, 0, -9)], [0], -3 * 10**30 + 27)
check(2, [(0, 1, 1, 10**30, -10**20)], [10**25, -10**25], -10**45)
check(2, [(0, 1, 0, 1, -1)], [1, -1], -1)
# 最短路反復で逆辺を使った割当の変更が必要。
check(6, [(0, 1, 0, 1, 0), (0, 2, 0, 1, 0),
          (1, 3, 0, 1, 0), (1, 4, 0, 1, 1),
          (2, 3, 0, 1, 1), (2, 4, 0, 1, 100),
          (3, 5, 0, 1, 0), (4, 5, 0, 1, 0)], [2, 0, 0, 0, 0, -2], 2)

# 需給の範囲指定（費用付き、"-inf" / "inf"、同じ頂点への複数指定）を全探索と比較する。
def balance_costs(n, edges):
    """需給ベクトルごとの辺の最小費用。"""
    best = {}
    for flows in product(*(range(e[2], e[3] + 1) for e in edges)):
        balance = [0] * n
        cost = 0
        for (u, v, lo, hi, c), f in zip(edges, flows):
            balance[u] += f
            balance[v] -= f
            cost += f * c
        key = tuple(balance)
        if key not in best or cost < best[key]:
            best[key] = cost
    return best


def acyclic(n, edges):
    """upper > lower の辺だけで閉路がないか。"""
    indegree = [0] * n
    active = [(u, v) for u, v, lo, hi, _ in edges if lo < hi]
    for _, v in active:
        indegree[v] += 1
    order = [v for v in range(n) if indegree[v] == 0]
    for u in order:
        for a, b in active:
            if a == u:
                indegree[b] -= 1
                if indegree[b] == 0:
                    order.append(b)
    return len(order) == n


def range_cost(ranges, y, window):
    """sum x_k = y、x_k は各範囲内（無制限側は [-window, window] で打ち切る）での sum c_k x_k の最小値。"""
    best = {0: 0}
    for lo, hi, c in ranges:
        lo = -window if lo == "-inf" else lo
        hi = window if hi == "inf" else hi
        nxt = {}
        for s, cost in best.items():
            for x in range(lo, hi + 1):
                if abs(s + x) <= 2 * window and (s + x not in nxt or cost + c * x < nxt[s + x]):
                    nxt[s + x] = cost + c * x
        best = nxt
    return best.get(y)


rng = Random(20261121)
tested = arbitrage = 0
for _ in range(400):
    n = rng.randrange(1, 4)
    edges = []
    for _ in range(rng.randrange(6)):
        lo = rng.randrange(3)
        edges.append((rng.randrange(n), rng.randrange(n), lo, lo + rng.randrange(3), rng.randrange(-4, 5)))
    exact = [rng.randrange(-3, 4) if rng.randrange(3) == 0 else 0 for _ in range(n)]
    ranges = [[] for _ in range(n)]
    for v in range(n):
        for _ in range(rng.randrange(3)):
            lo = "-inf" if rng.randrange(4) == 0 else rng.randrange(-4, 3)
            hi = "inf" if rng.randrange(4) == 0 else (lo if lo != "-inf" else -2) + rng.randrange(4)
            ranges[v].append((lo, hi, rng.randrange(-3, 4)))
    unbounded = any(cu < cd for v in range(n)
                    for i, (_, hu, cu) in enumerate(ranges[v]) if hu == "inf"
                    for j, (ld, _, cd) in enumerate(ranges[v]) if ld == "-inf" and i != j)
    best = balance_costs(n, edges)
    window = 3 * sum(e[3] for e in edges) + sum(abs(x) for x in exact) + 12
    costs = [{} for _ in range(n)]
    expected = None
    if not unbounded:
        for key, c in best.items():
            total = c
            for v in range(n):
                y = key[v] - exact[v]
                if y not in costs[v]:
                    costs[v][y] = range_cost(ranges[v], y, window)
                if costs[v][y] is None:
                    break
                total += costs[v][y]
            else:
                if expected is None or total < expected:
                    expected = total
    # dag=True では幅が正の負費用の範囲も負費用辺として数え、元の正容量の辺が DAG であることを要する。
    negative_range = any(c < 0 and not (isinstance(lo, int) and lo == hi) for rs in ranges for lo, hi, c in rs)
    allowed = dag_allowed(n, edges) and (not negative_range or acyclic(n, edges))
    modes = [(dense, False) for dense in (False, True)]
    if allowed:
        modes += [(dense, True) for dense in (False, True)]
    for dense, dag in modes:
        g = MinCostBFlow(n, dense=dense, dag=dag)
        for i, e in enumerate(edges):
            assert g.add_edge(*e) == i
        for v in range(n):
            g.add_balance(v, exact[v])
            for lo, hi, c in ranges[v]:
                g.add_balance_range(v, lo, hi, c)
        rejects(lambda: g.balance(0))
        if unbounded:
            rejects(g.solve)
            arbitrage += 1
            continue
        feasible, cost = g.solve()
        assert feasible == (expected is not None), (n, edges, exact, ranges)
        if not feasible:
            assert cost == 0
            rejects(lambda: g.balance(0))
            continue
        tested += 1
        assert cost == expected, (n, edges, exact, ranges, cost, expected)
        actual = [0] * n
        total = 0
        for (u, v, lo, hi, c), e in zip(edges, g.edges()):
            assert lo <= e.flow <= hi
            actual[u] += e.flow
            actual[v] -= e.flow
            total += e.flow * c
        assert actual == [g.balance(v) for v in range(n)]
        assert total + sum(range_cost(ranges[v], actual[v] - exact[v], window) for v in range(n)) == cost
        p = g.potential()
        for e in g.edges():
            reduced = e.cost + p[e.src] - p[e.dst]
            if e.flow < e.upper:
                assert reduced >= 0
            if e.flow > e.lower:
                assert reduced <= 0
assert tested >= 300 and arbitrage >= 10, (tested, arbitrage)

# 範囲の誤指定は拒否する。
g = MinCostBFlow(2)
rejects(lambda: g.add_balance_range(0, 3, 2))
rejects(lambda: g.add_balance_range(0, "inf", 2))
rejects(lambda: g.add_balance_range(0, 0, "-inf"))
# 非有界の判定: 費用が等しい組と、両側無制限の範囲 1 つは許す。同じ頂点に多数の範囲があっても線形時間。
g = MinCostBFlow(2)
g.add_balance_range(0, 0, "inf", 2)
g.add_balance_range(0, "-inf", 0, 2)
g.add_balance(1, -3)
g.add_edge(0, 1, 0, 5, 1)
assert g.solve() == (True, 9) and g.balance(0) == 3
g = MinCostBFlow(1)
g.add_balance_range(0, "-inf", "inf", -1)
assert g.solve() == (True, 0)
g = MinCostBFlow(1)
for _ in range(10**5):
    g.add_balance_range(0, "-inf", "inf", 0)
assert g.solve() == (True, 0)
g = MinCostBFlow(1)
g.add_balance_range(0, 0, "inf", 1)
g.add_balance_range(0, "-inf", 0, 2)
rejects(g.solve)
print("MinCostBFlow range tests:", tested, "feasible comparisons,", arbitrage, "unbounded rejections")
