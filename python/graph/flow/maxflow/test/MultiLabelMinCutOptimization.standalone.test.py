# competitive-verifier: STANDALONE

from itertools import product
from random import Random

from python.graph.flow.maxflow.MultiLabelMinCutOptimization import MultiLabelMinCutOptimization

INF = float("inf")


def rejects(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def random_costs(rng, k):
    return [rng.randint(-5, 5) for _ in range(k)]


def random_monge(rng, rows, cols):
    """単項 + w[x_i >= a][x_j < b] (w >= 0) の和は Monge。"""
    ui, uj = random_costs(rng, rows), random_costs(rng, cols)
    costs = [[ui[p] + uj[q] for q in range(cols)] for p in range(rows)]
    for _ in range(rng.randint(0, 3)):
        a, b, w = rng.randrange(1, rows + 1), rng.randrange(cols), rng.randint(0, 3)
        for p in range(a, rows):
            for q in range(b):
                costs[p][q] += w
    return costs


def add_random_term(rng, g, ks, terms):
    """g にランダムな項を加え、同じコストを terms に関数として記録する。"""
    n = len(ks)
    i, j = rng.randrange(n), rng.randrange(n)
    typ = rng.choice(["const", "unary", "ge_lt", "if_ge", "ge", "pge", "abs",
                      "convex", "pair", "pair_inf", "group"])
    if typ == "const":
        c = rng.randint(-5, 5)
        g.add_constant(c)
        terms.append(lambda x: c)
    elif typ == "unary":
        costs = [("inf" if rng.random() < 0.3 else rng.randint(-5, 5)) for _ in range(ks[i])]
        if all(c == "inf" for c in costs):
            rejects(lambda: g.add_unary(i, costs))
            return
        g.add_unary(i, costs)
        terms.append(lambda x: INF if costs[x[i]] == "inf" else costs[x[i]])
    elif typ in ("ge_lt", "if_ge"):
        if ks[i] < 2 or ks[j] < 2:
            return
        a, b = rng.randrange(1, ks[i]), rng.randrange(1, ks[j])
        if typ == "ge_lt":
            w = rng.randint(0, 4)
            g.add_penalty_ge_lt(i, a, j, b, w)
            terms.append(lambda x: w if x[i] >= a and x[j] < b else 0)
        else:
            g.add_if_ge_then_ge(i, a, j, b)
            terms.append(lambda x: INF if x[i] >= a and x[j] < b else 0)
    elif typ == "ge":
        d = rng.randint(-4, 4)
        if d >= ks[i] or (i == j and d > 0):
            rejects(lambda: g.add_ge(i, j, d))
            return
        g.add_ge(i, j, d)
        terms.append(lambda x: 0 if x[i] >= x[j] + d else INF)
    elif typ == "pge":
        d, w = rng.randint(-5, 5), rng.randint(0, 3)
        g.add_penalty_ge(i, j, d, w)
        terms.append(lambda x: w * max(0, x[j] + d - x[i]))
    elif typ == "abs":
        w = rng.randint(0, 3)
        g.add_abs_diff(i, j, w)
        terms.append(lambda x: w * abs(x[i] - x[j]))
    elif typ == "convex":
        a, b, c = rng.randint(0, 3), rng.randint(-3, 3), rng.randint(-3, 3)
        f = lambda d: a * d * d + b * d + c + (2 * abs(d) if a == 0 else 0)
        g.add_convex_diff(i, j, f)
        terms.append(lambda x: f(x[i] - x[j]))
    elif typ in ("pair", "pair_inf"):
        rows, cols = ks[i], ks[j]
        costs = random_monge(rng, rows, cols)
        if i == j:
            g.add_pairwise(i, j, costs)
            terms.append(lambda x: costs[x[i]][x[i]])
            return
        if typ == "pair_inf":
            # 右上に広がる階段状の禁止領域。半分は転置して左下にする。
            widths = sorted(rng.randint(0, cols) for _ in range(rows))
            widths[-1] = max(widths[-1], 1)
            costs = [[v if q < widths[p] else "inf" for q, v in enumerate(row)]
                     for p, row in enumerate(costs)]
            if rng.random() < 0.5:
                costs = [list(row) for row in zip(*costs)]
                i, j = j, i
        g.add_pairwise(i, j, costs)
        terms.append(lambda x: INF if costs[x[i]][x[j]] == "inf" else costs[x[i]][x[j]])
    else:
        conditions = []
        for _ in range(rng.randint(0, 3)):
            v = rng.randrange(n)
            if ks[v] >= 2:
                conditions.append((v, rng.randrange(1, ks[v])))
        amount = rng.randint(0, 4)
        kind = rng.randrange(4)
        if kind == 0:
            g.add_reward_all_ge(conditions, amount)
            terms.append(lambda x: -amount if all(x[v] >= a for v, a in conditions) else 0)
        elif kind == 1:
            g.add_reward_all_lt(conditions, amount)
            terms.append(lambda x: -amount if all(x[v] < a for v, a in conditions) else 0)
        elif kind == 2:
            g.add_penalty_any_ge(conditions, amount)
            terms.append(lambda x: amount if any(x[v] >= a for v, a in conditions) else 0)
        else:
            g.add_penalty_any_lt(conditions, amount)
            terms.append(lambda x: amount if any(x[v] < a for v, a in conditions) else 0)


def check(rng):
    n = rng.randint(1, 3)
    ks = [rng.randint(1, 4) for _ in range(n)]
    g = MultiLabelMinCutOptimization(ks)
    terms = []
    for _ in range(rng.randint(0, 6)):
        add_random_term(rng, g, ks, terms)
    evaluate = lambda x: sum(t(x) for t in terms)
    best = min(evaluate(x) for x in product(*map(range, ks)))
    if best == INF:
        rejects(g.solve)
        return False
    cost, x = g.solve()
    assert len(x) == n and all(0 <= v < k for v, k in zip(x, ks))
    assert cost == best == evaluate(x), (ks, cost, best, x)
    return True


rng = Random(20261120)
feasible = sum(check(rng) for _ in range(3000))
assert feasible >= 1000

# docstring の例。
g = MultiLabelMinCutOptimization([3, 3])
g.add_unary(0, [4, 1, 0])
g.add_ge(1, 0)
assert g.solve() == (0, [2, 2])

# 変数なし・単一ラベルのみ。
g = MultiLabelMinCutOptimization([])
g.add_constant(-7)
assert g.solve() == (-7, [])
g = MultiLabelMinCutOptimization([1, 1])
g.add_unary(0, [3])
g.add_abs_diff(0, 1, 5)
g.add_ge(0, 1)
assert g.solve() == (3, [0, 0])

# 階段状でない "inf" は拒否する。
g = MultiLabelMinCutOptimization([2, 2])
rejects(lambda: g.add_pairwise(0, 1, [[0, "inf"], ["inf", 0]]))
rejects(lambda: g.add_pairwise(0, 1, [["inf", "inf"], ["inf", "inf"]]))
print(f"MultiLabelMinCutOptimization: OK ({feasible} feasible random comparisons)")
