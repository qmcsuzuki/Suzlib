# competitive-verifier: STANDALONE

from itertools import product
from random import Random

from python.graph.flow.mincostflow.MinCostTension import MinCostTension


rng = Random(1729)
for _ in range(100):
    g = MinCostTension(3, dag=False)
    for v in (1, 2):
        g.add_bounds(0, v, -3, 3)
    a, b, c = [rng.randint(-3, 3) for _ in range(3)]
    g.add_abs(0, 1, a, 2)
    g.add_linear(0, 2, b)
    g.add_piecewise_linear(1, 2, [-2, 1], [-3, 0, 4], 7)
    g.add_discrete_convex(0, 2, -2, 2, lambda x: (x - c) ** 2)

    def objective(x, y):
        d = y - x
        return (2 * abs(x - a) + b * y + (y - c) ** 2 + 7
                + 3 * max(0, -2 - d) + 4 * max(0, d - 1))

    value = g.solve()
    assert value == min(objective(x, y) for x, y in product(range(-3, 4), range(-2, 3)))
    p, q, r = g.potentials()
    assert -3 <= q - p <= 3 and -2 <= r - p <= 2
    assert objective(q - p, r - p) == value

for dag in (False, True):
    g = MinCostTension(2, dag=dag)
    g.add_bounds(0, 1, upper=-2)
    g.add_linear(0, 1, -3)
    assert g.solve() == 6
    p, q = g.potentials()
    assert q - p == -2

for contradictory, linear in [(False, True), (True, False), (True, True)]:
    g = MinCostTension(4, dag=False)
    if contradictory:
        g.add_bounds(0, 1, 2, 1)
    if linear:
        g.add_linear(2, 3, 1)
    assert g.solve() is None
