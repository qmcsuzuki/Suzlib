# competitive-verifier: STANDALONE

from itertools import product
from random import Random

from python.graph.flow.MinCostBFlow import MinCostBFlow


def rejects(action):
    try:
        action()
    except AssertionError:
        return
    raise AssertionError('invalid call accepted')


def check(n, edges, balance, expected):
    for dense in (False, True):
        g = MinCostBFlow(n, dense=dense)
        for i, e in enumerate(edges):
            assert g.add_edge(*e) == i
        for v, b in enumerate(balance):
            g.add_balance(v, b + 1)
            g.add_balance(v, -1)
        rejects(g.edges)
        feasible, cost = g.solve()
        assert feasible == (expected is not None)
        assert cost == (0 if expected is None else expected)
        rejects(g.solve)
        rejects(lambda: g.add_balance(0, 0))
        rejects(lambda: g.add_edge(0, 0, 0, 0, 0))
        if not feasible:
            rejects(g.edges)
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
