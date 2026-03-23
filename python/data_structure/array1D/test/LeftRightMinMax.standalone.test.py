# competitive-verifier: STANDALONE

from python.data_structure.array1D.LeftRightMinMax import LeftRightMinMax

if __name__ == "__main__":
    for a in ([5], [3, 1, 4, 1, 5], [7, -2, 9, 0]):
        n = len(a)
        dat_min = LeftRightMinMax(a, min)
        dat_max = LeftRightMinMax(a, max)
        for i in range(n + 1):
            assert dat_min.minL(i) == min(a[:i], default=float("inf"))
            assert dat_min.minR(i) == min(a[i:], default=float("inf"))
            assert dat_max.maxL(i) == max(a[:i], default=-float("inf"))
            assert dat_max.maxR(i) == max(a[i:], default=-float("inf"))
        assert dat_min.all_prod() == min(a)
        assert dat_max.all_prod() == max(a)
        for i in range(n):
            b = a[:i] + a[i + 1:]
            assert dat_min.prod_without(i) == min(b, default=float("inf"))
            assert dat_max.prod_without(i) == max(b, default=-float("inf"))
        for l in range(n + 1):
            for r in range(l, n + 1):
                b = a[:l] + a[r:]
                assert dat_min.prod_outside(l, r) == min(b, default=float("inf"))
                assert dat_max.prod_outside(l, r) == max(b, default=-float("inf"))
