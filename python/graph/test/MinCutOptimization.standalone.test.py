# competitive-verifier: STANDALONE

from itertools import product
from random import Random

from python.graph.MinCutOptimization import MinCutOptimization


def brute_force(
    n,
    unary,
    pairwise,
    penalties,
    implications,
    forces,
):
    best = None
    best_x = None
    for x in product([False, True], repeat=n):
        if any(x[i] and not x[j] for i, j in implications):
            continue
        if any(x[i] != value for i, value in forces):
            continue

        cost = 0
        for i in range(n):
            cost += unary[i][x[i]]
        for i, j, costs in pairwise:
            cost += costs[(x[i] << 1) | x[j]]
        for i, j, penalty in penalties:
            if x[i] and not x[j]:
                cost += penalty

        if best is None or cost < best:
            best = cost
            best_x = x
    return best, best_x


def evaluate(x, unary, pairwise, penalties):
    cost = 0
    for i in range(len(x)):
        cost += unary[i][x[i]]
    for i, j, costs in pairwise:
        cost += costs[(x[i] << 1) | x[j]]
    for i, j, penalty in penalties:
        if x[i] and not x[j]:
            cost += penalty
    return cost


if __name__ == "__main__":
    rng = Random(91)

    for _ in range(1000):
        n = rng.randint(1, 6)
        opt = MinCutOptimization(n)

        unary = [[0, 0] for _ in range(n)]
        pairwise = []
        penalties = []
        implications = []
        forces = []

        for i in range(n):
            cost_false = rng.randint(-5, 5)
            cost_true = rng.randint(-5, 5)
            opt.add_unary(i, cost_false, cost_true)
            unary[i][0] += cost_false
            unary[i][1] += cost_true

            if rng.randrange(2):
                cost = rng.randint(-3, 3)
                opt.add_cost_true(i, cost)
                unary[i][1] += cost
            if rng.randrange(2):
                cost = rng.randint(-3, 3)
                opt.add_cost_false(i, cost)
                unary[i][0] += cost

        for i in range(n):
            for j in range(i + 1, n):
                if rng.randrange(3) == 0:
                    offset = rng.randint(-3, 3)
                    a = rng.randint(-3, 3)
                    b = rng.randint(-3, 3)
                    penalty = rng.randint(0, 5)
                    costs = (
                        offset,
                        offset + b,
                        offset + a + penalty,
                        offset + a + b,
                    )
                    opt.add_pairwise(i, j, *costs)
                    pairwise.append((i, j, costs))

                if rng.randrange(5) == 0:
                    penalty = rng.randint(0, 5)
                    opt.add_penalty(i, j, penalty)
                    penalties.append((i, j, penalty))

                if rng.randrange(8) == 0:
                    opt.add_implication(i, j)
                    implications.append((i, j))
                if rng.randrange(10) == 0:
                    opt.add_implication(j, i)
                    implications.append((j, i))

        for i in range(n):
            if rng.randrange(12) == 0:
                value = bool(rng.randrange(2))
                opt.force(i, value)
                forces.append((i, value))

        expected, _ = brute_force(
            n,
            unary,
            pairwise,
            penalties,
            implications,
            forces,
        )

        if expected is None:
            try:
                opt.solve()
            except ValueError:
                pass
            else:
                assert False
            continue

        actual, x = opt.solve()
        assert actual == expected
        assert evaluate(x, unary, pairwise, penalties) == expected
        assert all(not x[i] or x[j] for i, j in implications)
        assert all(x[i] == value for i, value in forces)

    # Non-submodular pairwise costs cannot be represented by an s-t cut.
    opt = MinCutOptimization(2)
    try:
        opt.add_pairwise(0, 1, 0, 0, 0, 1)
    except AssertionError:
        pass
    else:
        assert False
