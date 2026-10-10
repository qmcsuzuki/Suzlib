# competitive-verifier: STANDALONE

from itertools import product
from random import Random

from python.math.number_theory.IntegerProgramming2Variables import (
    integer_problem_2variables,
    knapsack_2variable,
    knapsack_dual_2variable,
)


def brute_ilp(a, b, s, t, u, L, R):
    return max(a * x + max(0, b) * ((u - s * x) // t)
               for x in range(L, R + 1) if s * x <= u)


def brute_max(v1, v2, w1, w2, W):
    return max(v1 * x + v2 * ((W - w1 * x) // w2)
               for x in range(W // w1 + 1))


def brute_min(v1, v2, w1, w2, W):
    return min(v1 * x + v2 * max(0, (W - w1 * x + w2 - 1) // w2)
               for x in range((W + w1 - 1) // w1 + 1))


if __name__ == '__main__':
    # 負の目的係数、負の L、s=0、区間末端を含むケース。
    for a, b in product(range(-2, 3), repeat=2):
        for s, t in product(range(4), range(1, 5)):
            for L in range(-2, 3):
                for R in range(L, L + 4):
                    for u in range(s * L, s * L + 5):
                        assert integer_problem_2variables(a, b, s, t, u, L, R) == brute_ilp(a, b, s, t, u, L, R)

    for v1, v2 in product(range(6), repeat=2):
        for w1, w2 in product(range(1, 8), repeat=2):
            for W in range(30):
                assert knapsack_2variable(v1, v2, w1, w2, W) == brute_max(v1, v2, w1, w2, W)
                assert knapsack_dual_2variable(v1, v2, w1, w2, W) == brute_min(v1, v2, w1, w2, W)

    rng = Random(20261010)
    for _ in range(10000):
        a, b = rng.randrange(-1000, 1000), rng.randrange(-1000, 1000)
        s, t = rng.randrange(1000), rng.randrange(1, 1000)
        L = rng.randrange(-1000, 1000)
        R = L + rng.randrange(200)
        u = rng.randrange(s * L, s * L + 100000)
        assert integer_problem_2variables(a, b, s, t, u, L, R) == brute_ilp(a, b, s, t, u, L, R)

    for _ in range(10000):
        v1, v2 = rng.randrange(10**9), rng.randrange(10**9)
        w1, w2 = rng.randrange(1, 10**9), rng.randrange(1, 10**9)
        W = rng.randrange(10**18)
        assert knapsack_2variable(v1, v2, w1, w2, W) >= 0
        assert knapsack_dual_2variable(v1, v2, w1, w2, W) >= 0
