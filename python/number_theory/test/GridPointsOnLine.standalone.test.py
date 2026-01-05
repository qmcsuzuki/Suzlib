# competitive-verifier: STANDALONE

from itertools import product

from python.number_theory.GridPointsOnLine import grid_points_on_line


def brute(a, b, c, L, n, R, m):
    cnt = 0
    for x in range(L, n + 1):
        for y in range(R, m + 1):
            if a * x + b * y == c:
                cnt += 1
    return cnt


if __name__ == "__main__":
    n, m = 8, 10
    for a, b, c in product(range(-5, 5), repeat=3):
        if b == 0:
            continue
        for L, R in product(range(-3, 3), repeat=2):
            res1 = grid_points_on_line(a, b, c, L, n, R, m)
            res2 = brute(a, b, c, L, n, R, m)
            assert res1[1] - res1[0] == res2
