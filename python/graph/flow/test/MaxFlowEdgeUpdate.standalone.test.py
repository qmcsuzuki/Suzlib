# competitive-verifier: STANDALONE

from itertools import product
from random import Random

from python.graph.flow.MaxFlow import MFGraph


def balance(n, edges, flows):
    result = [0] * n
    for (u, v, c), f in zip(edges, flows):
        result[u] += f
        result[v] -= f
    return result


def check(g, edges, expected):
    actual = g.edges()
    assert [(e.src, e.dst, e.cap) for e in actual] == edges
    assert all(0 <= e.flow <= e.cap for e in actual)
    assert balance(g._n, edges, [e.flow for e in actual]) == expected


# 任意の収支、最大流、途中の s-t フローを始状態にする。
# 自己ループ・平行辺・逆向きの元辺・容量0を含め、全列挙と照合する。
rng = Random(3010)
for trial in range(600):
    n = rng.randrange(2, 5)
    edges = [(rng.randrange(n), rng.randrange(n), rng.randrange(3))
             for _ in range(rng.randrange(1, 8))]
    g = MFGraph(n)
    for i, (u, v, c) in enumerate(edges):
        g.add_edge(u, v, c)
        if trial % 3 == 0:
            g.change_edge(i, c, rng.randrange(c + 1))
    if trial % 3 == 1:
        g.flow(0, n - 1)
    elif trial % 3 == 2:
        g.flow(0, n - 1, rng.randrange(3))
    expected = balance(n, edges, [e.flow for e in g.edges()])
    feasible = [f for f in product(*(range(c + 1) for u, v, c in edges))
                if balance(n, edges, f) == expected]
    for _ in range(20):
        i = rng.randrange(len(edges))
        old = g.get_edge(i)
        limit = rng.choice([None, 0, 1, 2, 10])
        increase = rng.randrange(2)
        if increase:
            available = max(f[i] for f in feasible) - old.flow
            current = g.increase_edge(i, limit)
            delta = current - old.flow
        else:
            available = old.flow - min(f[i] for f in feasible)
            current = g.decrease_edge(i, limit)
            delta = old.flow - current
        assert current == g.get_edge(i).flow
        assert delta == (available if limit is None else min(limit, available))
        check(g, edges, expected)
    if trial % 3 == 1:
        assert g.flow(0, n - 1) == 0

# 容量縮小に必要な量を迂回できない場合も、途中までの変更が残る。
g = MFGraph(3)
i = g.add_edge(0, 2, 5)
assert g.flow(0, 2) == 5
g.add_edge(0, 1, 2)
g.add_edge(1, 2, 2)
assert g.decrease_edge(i, 4) == 3
assert g.get_edge(i).flow == 3
check(g, [(0, 2, 5), (0, 1, 2), (1, 2, 2)], [5, 0, -5])
g.change_edge(i, 3, 3)
assert g.flow(0, 2) == 0
assert g.flow(2, 0, 4) == 4
check(g, [(0, 2, 3), (0, 1, 2), (1, 2, 2)], [1, 0, -1])

# 自己ループ・巨大容量・上限・入力チェック。
g = MFGraph(1)
i = g.add_edge(0, 0, 10**30)
assert g.increase_edge(i, 10**20) == 10**20
assert g.increase_edge(i) == 10**30
assert g.increase_edge(i, 0) == 10**30
assert g.increase_edge(i) == 10**30
assert g.decrease_edge(i, 0) == 10**30
assert g.decrease_edge(i, 10**20) == 10**30 - 10**20
assert g.decrease_edge(i) == 0
for method in (g.increase_edge, g.decrease_edge):
    for args in [(-1,), (1,), (0, -1)]:
        try:
            method(*args)
        except AssertionError:
            pass
        else:
            raise AssertionError('invalid call accepted')
