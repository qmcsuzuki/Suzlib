# competitive-verifier: STANDALONE

import python.matrix.DeterminantMatrixLinearExpression as dmle
from itertools import permutations
from random import Random


def brute(M0, M1, MOD):
    n = len(M0)
    res = [0] * (n + 1)
    for p in permutations(range(n)):
        f = [1]
        for i in range(n):
            a = M0[i][p[i]] % MOD
            b = M1[i][p[i]] % MOD
            g = [0] * (len(f) + 1)
            for j, v in enumerate(f):
                g[j] = (g[j] + a * v) % MOD
                g[j + 1] = (g[j + 1] + b * v) % MOD
            f = g

        inv = 0
        for i in range(n):
            for j in range(i + 1, n):
                inv += p[i] > p[j]
        sign = -1 if inv & 1 else 1
        for i, v in enumerate(f):
            res[i] = (res[i] + sign * v) % MOD
    return res


rng = Random(0)
for MOD in (2, 3, 5, 101, 998244353):
    dmle.MOD = MOD
    for n in range(7):
        for _ in range(8):
            M0 = [[rng.randrange(MOD) for _ in range(n)] for _ in range(n)]
            M1 = [[rng.randrange(MOD) for _ in range(n)] for _ in range(n)]
            M0_copy = [row[:] for row in M0]
            M1_copy = [row[:] for row in M1]
            assert dmle.determinant_matrix_linear_expression(M0, M1) == brute(
                M0, M1, MOD
            )
            assert M0 == M0_copy
            assert M1 == M1_copy
