# competitive-verifier: STANDALONE

from itertools import product

from python.math.number_theory.ModularLatticeHull import (
    lattice_prefix_min,
    lattice_prefix_min_hull,
    lattice_lower_convex_hull,
    under_line_upper_hull,
    in_triangle,
    out_of_triangle,
)


def brute_hull(points, lower=True):
    hull = []
    for p in points:
        while len(hull) > 1:
            x0, y0 = hull[-2]
            x1, y1 = hull[-1]
            cross = (x1 - x0) * (p[1] - y1) - (y1 - y0) * (p[0] - x1)
            if (cross > 0) if lower else (cross < 0):
                break
            hull.pop()
        hull.append(p)
    return hull


def brute_max(v1, v2, w1, w2, W):
    return max(v1 * x + v2 * ((W - w1 * x) // w2)
               for x in range(W // w1 + 1))


def brute_min(v1, v2, w1, w2, W):
    return min(v1 * x + v2 * max(0, (W - w1 * x + w2 - 1) // w2)
               for x in range((W + w1 - 1) // w1 + 1))


if __name__ == '__main__':
    for M in range(1, 21):
        for A in range(-12, 13):
            for B in range(-3, 5):
                for R in range(21):
                    xs, steps = lattice_prefix_min(M, A, B, R)
                    assert xs == lattice_prefix_min_hull(M, A, B, R)
                    records, mn = [], M
                    for x in range(R + 1):
                        y = (A * x + B) % M
                        if y < mn:
                            records.append((x, y))
                            mn = y
                    assert [(x, (A*x+B) % M) for x in xs] == brute_hull(records)
                    assert len(xs) == len(steps) + 1
                    for i, (dx, dy) in enumerate(steps):
                        x0, x1 = xs[i:i+2]
                        y0, y1 = (A*x0+B) % M, (A*x1+B) % M
                        assert dx > 0 and (x1-x0) % dx == 0
                        assert (y1-y0)*dx == (x1-x0)*dy

    for M in range(1, 13):
        for A in range(-12, 13):
            for B in range(-3, 5):
                for L in range(-2, 3):
                    for R in range(L, L + 6):
                        xs, steps = lattice_lower_convex_hull(M, A, B, L, R)
                        expected = brute_hull([(x, (A*x+B) % M) for x in range(L, R+1)])
                        assert [(x, (A*x+B) % M) for x in xs] == expected
                        assert len(xs) == len(steps) + 1
                        for i, (dx, dy) in enumerate(steps):
                            x0, x1 = xs[i:i+2]
                            y0, y1 = (A*x0+B) % M, (A*x1+B) % M
                            assert dx > 0 and (x1-x0) % dx == 0
                            assert (y1-y0)*dx == (x1-x0)*dy

    for a in range(-4, 5):
        for b in range(1, 8):
            for N in range(-4, 6):
                for L in range(-3, 4):
                    for width in range(8):
                        R = L + width
                        xs, ys, dxs = under_line_upper_hull(a, b, N, L, R)
                        expected = brute_hull([(x, (N-a*x)//b) for x in range(L, R+1)], lower=False)
                        assert list(zip(xs, ys)) == expected
                        assert len(xs) == len(dxs) + 1
                        assert all(dx > 0 and (xs[i+1]-xs[i]) % dx == 0 for i, dx in enumerate(dxs))

    for a, b in product(range(1, 9), repeat=2):
        for N in range(24):
            xs, ys = in_triangle(a, b, N)
            assert all(a*x+b*y <= N for x, y in zip(xs, ys))
            xs, ys = out_of_triangle(a, b, N)
            assert all(a*x+b*y >= N for x, y in zip(xs, ys))
            for p, q in product(range(4), repeat=2):
                xs, ys = in_triangle(a, b, N)
                assert max(p*x+q*y for x, y in zip(xs, ys)) == brute_max(p, q, a, b, N)
                xs, ys = out_of_triangle(a, b, N)
                assert min(p*x+q*y for x, y in zip(xs, ys)) == brute_min(p, q, a, b, N)
