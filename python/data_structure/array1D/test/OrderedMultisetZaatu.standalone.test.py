# competitive-verifier: STANDALONE

from python.data_structure.array1D.OrderedMultisetZaatu import OrderedMultisetWithZaatu


def brute_count_less(values, v):
    return sum(1 for x in values if x < v)


def brute_count_ge(values, v):
    return sum(1 for x in values if x >= v)


if __name__ == "__main__":
    cand = [-8, -3, 0, 2, 4, 10]
    S = OrderedMultisetWithZaatu(cand, -10, 20)

    values = [-3, 0, 0, 4, 10]
    for x in values:
        S.add(x)

    for v in range(-20, 31):
        assert S.count_less(v) == brute_count_less(values, v)
        assert S.count_ge(v) == brute_count_ge(values, v)

    S.delete(0)
    values.remove(0)
    S.add(2)
    values.append(2)

    for v in range(-20, 31):
        assert S.count_less(v) == brute_count_less(values, v)
        assert S.count_ge(v) == brute_count_ge(values, v)
