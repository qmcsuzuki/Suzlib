# competitive-verifier: STANDALONE

from itertools import product
from random import Random

from python.graph.flow.MaxFlow import MFGraph


def balance(n, edges, flows):
    b = [0] * n
    for (u, v, c), f in zip(edges, flows):
        b[u] += f
        b[v] -= f
    return b


def min_cut_value(n, edges, s, t):
    return min(sum(c for u, v, c in edges
                   if mask >> u & 1 and not (mask >> v & 1))
               for mask in range(1 << n)
               if mask >> s & 1 and not (mask >> t & 1))


def check(g, edges, s, t, value):
    actual = g.edges()
    assert [(e.src, e.dst, e.cap) for e in actual] == edges
    assert all(0 <= e.flow <= e.cap for e in actual)
    expected = [0] * g._n
    expected[s], expected[t] = value, -value
    assert balance(g._n, edges, [e.flow for e in actual]) == expected
    assert value == min_cut_value(g._n, edges, s, t)


# 全列挙で最大フローを選び、Dinic の経路選択に依存しない循環入りの状態も試す。
rng = Random(3110)
for _ in range(400):
    n = rng.randrange(2, 6)
    s, t = rng.sample(range(n), 2)
    edges = [(rng.randrange(n), rng.randrange(n), rng.randrange(3))
             for _ in range(rng.randrange(1, 8))]
    value = min_cut_value(n, edges, s, t)
    expected = [0] * n
    expected[s], expected[t] = value, -value
    feasible = [f for f in product(*(range(c + 1) for u, v, c in edges))
                if balance(n, edges, f) == expected]
    initial = rng.choice(feasible)
    g = MFGraph(n)
    for i, ((u, v, c), f) in enumerate(zip(edges, initial)):
        g.add_edge(u, v, c)
        g.change_edge(i, c, f)
    for _ in range(20):
        i = rng.randrange(len(edges))
        u, v, c = edges[i]
        new_cap = rng.randrange(4)
        value += g.change_capacity(i, new_cap, s, t)
        edges[i] = (u, v, new_cap)
        check(g, edges, s, t, value)

# s,t と切り離された循環の削除は総流量を減らさない。
g = MFGraph(4)
g.add_edge(0, 3, 5)
a = g.add_edge(1, 2, 7)
b = g.add_edge(2, 1, 7)
g.change_edge(a, 7, 7)
g.change_edge(b, 7, 7)
assert g.flow(0, 3) == 5
assert g.change_capacity(a, 0, 0, 3) == 0
assert g.get_edge(b).flow == 0

# 一部だけ迂回でき、残りをキャンセルする。始点・終点に接する辺も更新。
g = MFGraph(4)
g.add_edge(0, 1, 10)
e = g.add_edge(1, 2, 10)
g.add_edge(2, 3, 10)
assert g.flow(0, 3) == 10
alt = g.add_edge(1, 2, 3)
assert g.change_capacity(e, 2, 0, 3) == -5
assert g.get_edge(alt).flow == 3
assert g.change_capacity(0, 0, 0, 3) == -5
assert g.change_capacity(0, 10**30, 0, 3) == 5
assert g.change_capacity(2, 0, 0, 3) == -5
assert g.change_capacity(2, 10**30, 0, 3) == 5
assert g.change_capacity(e, 10**30, 0, 3) == 10**30 - 5
assert g.change_capacity(e, 0, 0, 3) == -(10**30 - 3)

# 無向辺の両方向を順に削除・復活させる。
g = MFGraph(3)
ids = []
for u, v in [(0, 1), (1, 2), (0, 2)]:
    ids.append((g.add_edge(u, v, 1), g.add_edge(v, u, 1)))
value = g.flow(0, 2)
assert value == 2
for cap, expected in [(0, 1), (1, 2), (0, 1)]:
    for e in ids[0]:
        value += g.change_capacity(e, cap, 0, 2)
    assert value == expected
