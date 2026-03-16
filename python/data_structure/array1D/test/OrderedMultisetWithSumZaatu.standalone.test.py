# competitive-verifier: STANDALONE

import random

from python.data_structure.array1D.OrderedMultisetZaatu import OrderedMultisetWithSumWithZaatu


def brute_sum_less(values, v):
    return sum(x for x in values if x < v)


def brute_sum_ge(values, v):
    return sum(x for x in values if x >= v)


def brute_sum_smallest_k(values, k):
    return sum(sorted(values)[:k])


def brute_sum_top_k(values, k):
    return sum(sorted(values, reverse=True)[:k])



def brute_sum_eq(values, v):
    return sum(x for x in values if x == v)


if __name__ == "__main__":
    random.seed(0)

    cand = [-8, -3, 0, 2, 4, 10]
    S = OrderedMultisetWithSumWithZaatu(cand, -10, 20)
    values = []

    for _ in range(500):
        t = random.randrange(2)

        if t == 0 or not values:
            x = random.choice(cand)
            S.add(x)
            values.append(x)
        else:
            x = random.choice(values)
            S.delete(x)
            values.remove(x)

        assert len(S) == len(values)
        assert S.total_sum == sum(values)

        for v in range(-20, 31):
            assert S.sum_less(v) == brute_sum_less(values, v)
            assert S.sum_ge(v) == brute_sum_ge(values, v)
            assert S.sum_eq(v) == brute_sum_eq(values, v)

        for k in range(0, len(values) + 2):
            kk = min(k, len(values))
            assert S.sum_smallest_k(k) == brute_sum_smallest_k(values, kk)
            assert S.sum_top_k(k) == brute_sum_top_k(values, kk)

    # k > len(self) は全要素和に丸められる
    assert S.sum_smallest_k(len(values) + 5) == sum(values)
    assert S.sum_top_k(len(values) + 5) == sum(values)

    try:
        S.sum_smallest_k(-1)
        assert False
    except AssertionError:
        pass

    try:
        S.sum_top_k(-1)
        assert False
    except AssertionError:
        pass
