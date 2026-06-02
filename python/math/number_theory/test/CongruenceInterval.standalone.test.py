# competitive-verifier: STANDALONE

from python.math.number_theory.CongruenceInterval import residue_range


def brute(L, R, r, m):
    xs = [x for x in range(L, R) if x % m == r % m]
    if not xs:
        return 0, None, None
    return len(xs), xs[0], xs[-1]


if __name__ == "__main__":
    for L in range(-10, 11):
        for R in range(-10, 11):
            for r in range(-15, 16):
                for m in range(1, 12):
                    count, x_min, x_max = residue_range(L, R, r, m)
                    expected_count, expected_min, expected_max = brute(L, R, r, m)
                    assert count == expected_count
                    if count:
                        assert x_min == expected_min
                        assert x_max == expected_max
                        assert x_min % m == r % m
                        assert x_max % m == r % m
                        assert L <= x_min <= x_max < R
