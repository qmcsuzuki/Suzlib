# competitive-verifier: STANDALONE

from itertools import product
from random import Random

from python.graph.flow.maxflow.BFlow import BFlow
from python.graph.flow.maxflow.LowerBoundSTFlow import LowerBoundSTFlow


def enumerate_flows(n, edges):
    for flows in product(*(range(lo, hi + 1) for u, v, lo, hi in edges)):
        balance = [0] * n
        for (u, v, lo, hi), f in zip(edges, flows):
            balance[u] += f
            balance[v] -= f
        yield flows, balance


def check(g, edges, balance):
    result = g.edges()
    assert len(result) == len(edges)
    actual = [0] * len(balance)
    for i, ((u, v, lo, hi), e) in enumerate(zip(edges, result)):
        assert e == g.get_edge(i)
        assert (e.src, e.dst, e.lower, e.upper) == (u, v, lo, hi)
        assert lo <= e.flow <= hi
        actual[u] += e.flow
        actual[v] -= e.flow
    assert actual == balance


def rejects(action):
    try:
        action()
    except AssertionError:
        return
    raise AssertionError('invalid call accepted')


rng = Random(2910)
for _ in range(500):
    n = rng.randrange(1, 5)
    edges = []
    for j in range(rng.randrange(7)):
        lo = rng.randrange(3)
        edges.append((rng.randrange(n), rng.randrange(n), lo, lo + rng.randrange(3)))
    candidates = list(enumerate_flows(n, edges))
    if rng.randrange(2):
        balance = rng.choice(candidates)[1]
    else:
        balance = [rng.randrange(-3, 4) for v in range(n)]
        if rng.randrange(2):
            balance[-1] -= sum(balance)
    feasible = [f for f, b in candidates if b == balance]
    g = BFlow(n)
    for i, e in enumerate(edges):
        assert g.add_edge(*e) == i
    for v, b in enumerate(balance):
        g.add_balance(v, b + 1)
        g.add_balance(v, -1)
    rejects(g.edges)
    assert g.solve() == bool(feasible)
    rejects(g.solve)
    rejects(lambda: g.add_balance(0, 1))
    rejects(lambda: g.add_edge(0, 0, 0, 1))
    if not feasible:
        rejects(g.edges)
        continue
    check(g, edges, balance)
    order = list(range(len(edges))) * 2
    rng.shuffle(order)
    for i in order:
        snapshot = g.edges()
        saved = [tuple(e) for e in snapshot]
        assert g.maximize_edge(i) == max(f[i] for f in feasible)
        check(g, edges, balance)
        assert [tuple(e) for e in snapshot] == saved
        assert g.minimize_edge(i) == min(f[i] for f in feasible)
        check(g, edges, balance)

for _ in range(500):
    n = rng.randrange(2, 5)
    s, t = rng.sample(range(n), 2)
    edges = []
    for j in range(rng.randrange(7)):
        lo = rng.randrange(3)
        edges.append((rng.randrange(n), rng.randrange(n), lo, lo + rng.randrange(3)))
    lower = rng.randrange(5)
    upper = None if rng.randrange(2) else lower + rng.randrange(5)
    feasible = []
    for f, b in enumerate_flows(n, edges):
        value = b[s]
        if value < lower or (upper is not None and value > upper):
            continue
        if b[t] == -value and all(b[v] == 0 for v in range(n) if v not in (s, t)):
            feasible.append(value)
    g = LowerBoundSTFlow(n, s, t)
    for i, e in enumerate(edges):
        assert g.add_edge(*e) == i
    rejects(g.edges)
    assert g.solve(lower, upper) == bool(feasible)
    rejects(g.solve)
    rejects(lambda: g.add_edge(s, t, 0, 1))
    if not feasible:
        rejects(g.maximize)
        rejects(g.minimize)
        rejects(g.edges)
        continue
    for method, expected in [(g.maximize, max(feasible)), (g.minimize, min(feasible)),
                             (g.maximize, max(feasible))]:
        assert method() == expected
        balance = [0] * n
        balance[s], balance[t] = expected, -expected
        check(g, edges, balance)

# 需給の範囲指定。全流量の列挙を範囲で絞り込み、実行可能性・需給と辺の最大化/最小化を比較する。
def check_range(g, edges, lo, hi, n):
    result = g.edges()
    actual = [0] * n
    for (u, v, a, b), e in zip(edges, result):
        assert (e.src, e.dst, e.lower, e.upper) == (u, v, a, b) and a <= e.flow <= b
        actual[u] += e.flow
        actual[v] -= e.flow
    assert actual == [g.balance(v) for v in range(n)]
    assert all(l <= x <= h for l, x, h in zip(lo, actual, hi))


INF = 10**9
for _ in range(1500):
    n = rng.randrange(1, 5)
    edges = []
    for j in range(rng.randrange(7)):
        a = rng.randrange(3)
        edges.append((rng.randrange(n), rng.randrange(n), a, a + rng.randrange(3)))
    g = BFlow(n)
    for i, e in enumerate(edges):
        assert g.add_edge(*e) == i
    lo, hi = [0] * n, [0] * n
    for v in range(n):
        # 整数範囲・片側無制限・両側無制限・add_balance との和を混ぜる。
        for _ in range(rng.randrange(3)):
            kind = rng.randrange(4)
            if kind == 0:
                x = rng.randrange(-3, 4)
                g.add_balance(v, x)
                lo[v] += x
                hi[v] += x
            else:
                a = "-inf" if kind == 3 or rng.randrange(4) == 0 else rng.randrange(-4, 3)
                b = "inf" if kind == 3 or rng.randrange(4) == 0 else (a if a != "-inf" else -2) + rng.randrange(4)
                g.add_balance_range(v, a, b)
                lo[v] = -INF if a == "-inf" or lo[v] == -INF else lo[v] + a
                hi[v] = INF if b == "inf" or hi[v] == INF else hi[v] + b
    feasible = [(f, b) for f, b in enumerate_flows(n, edges)
                if all(l <= x <= h for l, x, h in zip(lo, b, hi))]
    rejects(lambda: g.balance(0))
    assert g.solve() == bool(feasible), (n, edges, lo, hi)
    if not feasible:
        rejects(lambda: g.balance(0))
        rejects(lambda: g.maximize_balance(0))
        continue
    check_range(g, edges, lo, hi, n)
    ops = [("bmax", v) for v in range(n)] + [("bmin", v) for v in range(n)]
    ops += [("emax", i) for i in range(len(edges))] + [("emin", i) for i in range(len(edges))]
    ops *= 2
    rng.shuffle(ops)
    for op, x in ops:
        if op == "bmax":
            assert g.maximize_balance(x) == max(b[x] for f, b in feasible) == g.balance(x)
        elif op == "bmin":
            assert g.minimize_balance(x) == min(b[x] for f, b in feasible) == g.balance(x)
        elif op == "emax":
            assert g.maximize_edge(x) == max(f[x] for f, b in feasible)
        else:
            assert g.minimize_edge(x) == min(f[x] for f, b in feasible)
        check_range(g, edges, lo, hi, n)

# 範囲の誤指定は拒否する。
g = BFlow(2)
rejects(lambda: g.add_balance_range(0, 3, 2))
rejects(lambda: g.add_balance_range(0, "inf", 2))
rejects(lambda: g.add_balance_range(0, 0, "-inf"))
# 無制限側は接続辺の上限の和で置き換えるので、巨大容量でも正確な値を返す。
g = BFlow(2)
g.add_balance_range(0, "-inf", "inf")
g.add_balance_range(1, "-inf", "inf")
g.add_edge(0, 1, 0, 10**30)
assert g.solve()
assert g.maximize_balance(0) == 10**30 and g.balance(1) == -10**30
assert g.minimize_balance(0) == 0 and g.minimize_balance(1) == -10**30

# 空グラフ、固定辺、巨大容量、非負の s-t 流量が存在しない場合。
g = BFlow(0)
assert g.solve() and g.edges() == []
g = BFlow(1)
e = g.add_edge(0, 0, 7, 10**30)
assert g.solve()
assert g.maximize_edge(e) == 10**30
assert g.minimize_edge(e) == 7
for lower, upper, expected in [(0, None, True), (1, None, False), (0, 0, True)]:
    g = LowerBoundSTFlow(2, 0, 1)
    assert g.solve(lower, upper) == expected
    if expected:
        assert g.maximize() == g.minimize() == 0
        assert g.edges() == []
g = LowerBoundSTFlow(2, 0, 1)
g.add_edge(1, 0, 1, 1)
assert not g.solve()
g = LowerBoundSTFlow(2, 0, 1)
g.add_edge(0, 1, 0, 10**30)
assert g.solve(10**20, 10**20)
assert g.maximize() == g.minimize() == 10**20
