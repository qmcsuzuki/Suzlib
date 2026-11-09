# competitive-verifier: STANDALONE

from itertools import product
from random import Random

from python.graph.flow.mincostflow.MinCostFlow import MCFGraph, DAGMCFGraph


def brute_flow(n, edges, s, t):
    costs = {}
    for flows in product(*(range(cap + 1) for _, _, cap, _ in edges)):
        balance = [0] * n
        cost = 0
        for (u, v, _, c), f in zip(edges, flows):
            balance[u] -= f
            balance[v] += f
            cost += c * f
        f = balance[t]
        if f < 0 or balance[s] != -f:
            continue
        if any(balance[v] for v in range(n) if v not in (s, t)):
            continue
        costs[f] = min(costs.get(f, cost), cost)
    return costs


def check(n, edges, s, t, dag=True):
    expected = brute_flow(n, edges, s, t)
    for dense in (False, True):
        for limit in (None, 0, 1, 2, max(expected), max(expected) + 1):
            for method in ('min_cost_flow', 'flow', 'slope'):
                g = DAGMCFGraph(n, s, t, dense) if dag else MCFGraph(n, dense)
                for e in edges:
                    g.add_edge(*e)
                args = (limit,) if dag else (s, t, limit)
                result = getattr(g, method)(*args)
                feasible = {f: c for f, c in expected.items() if limit is None or f <= limit}
                if method == 'min_cost_flow':
                    want = min(feasible.items(), key=lambda item: (item[1], item[0]))
                else:
                    f = max(feasible)
                    want = (f, feasible[f])
                if method == 'slope':
                    assert result[0] == (0, 0)
                    for (a, ca), (b, cb) in zip(result, result[1:]):
                        assert a < b and (cb - ca) % (b - a) == 0
                        for f in range(a, b + 1):
                            assert ca + (cb - ca) // (b - a) * (f - a) == feasible[f]
                    result = result[-1]
                assert result == want, (edges, limit, method, result, want)
                balance = [0] * n
                cost = 0
                for i, e in enumerate(g.edges()):
                    assert e == g.get_edge(i)
                    assert (e.src, e.dst, e.cap, e.cost) == edges[i]
                    assert 0 <= e.flow <= e.cap
                    balance[e.src] -= e.flow
                    balance[e.dst] += e.flow
                    cost += e.flow * e.cost
                assert cost == result[1]
                assert balance[s] == -result[0] and balance[t] == result[0]
                assert all(balance[v] == 0 for v in range(n) if v not in (s, t))
                for again in ('flow', 'slope', 'min_cost_flow'):
                    try:
                        getattr(g, again)(*args)
                    except AssertionError:
                        pass
                    else:
                        raise AssertionError('second solve must fail')


if __name__ == '__main__':
    # 負・ゼロ・正の限界費用、同費用の最小流量、容量途中での打ち切り。
    check(2, [(0, 1, 3, -5), (0, 1, 2, 0), (0, 1, 1, 4)], 0, 1)
    check(2, [], 0, 1)
    check(3, [(0, 1, 2, -5)], 0, 2)
    # 到達不能な頂点や容量ゼロの辺も初期ポテンシャルに影響する。
    check(4, [(0, 3, 2, -1), (1, 3, 0, -100)], 0, 3)
    # 2 単位目で逆辺を使い、最初の割り当てを変更する。
    check(6, [(4, 0, 1, 0), (4, 1, 1, 0), (2, 5, 1, 0),
              (3, 5, 1, 0), (0, 2, 1, -10), (0, 3, 1, -9),
              (1, 2, 1, -9)], 4, 5)
    # practice2_e 型。最大流量 6 の費用 -30 に対し、最適は流量 4、費用 -40。
    edges = [(6, i, 2, 0) for i in range(3)]
    edges += [(j + 3, 7, 2, 0) for j in range(3)]
    edges += [(i, j + 3, 1, -10 if i < 2 and j < 2 else 0)
              for i in range(3) for j in range(3)]
    check(8, edges, 6, 7)
    rng = Random(20261102)
    for _ in range(300):
        n = rng.randrange(2, 6)
        s, t = n - 1, 0
        order = [s] + list(range(1, n - 1)) + [t]
        edges = []
        for _ in range(rng.randrange(8)):
            i, j = sorted(rng.sample(range(n), 2))
            edges.append((order[i], order[j], rng.randrange(3), rng.randrange(-5, 6)))
        check(n, edges, s, t)
        edges = [(rng.randrange(n), rng.randrange(n), rng.randrange(3), rng.randrange(6))
                 for _ in range(rng.randrange(8))]
        check(n, edges, 0, n - 1, False)
