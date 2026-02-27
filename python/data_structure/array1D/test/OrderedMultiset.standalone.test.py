# competitive-verifier: STANDALONE

from python.data_structure.array1D.OrderedMultiset import OrderedMultiset


def brute_count_less(values, v):
    return sum(1 for x in values if x < v)


def brute_count_ge(values, v):
    return sum(1 for x in values if x >= v)


if __name__ == "__main__":
    banhei_min, banhei_max = -1, 8
    S = OrderedMultiset(banhei_min, banhei_max)
    values = [0, 2, 2, 5, 7]
    for x in values:
        S.add(x)
    assert len(S) == len(values)

    for v in range(-5, 15):
        assert S.count_less(v) == brute_count_less(values, v)
        assert S.count_ge(v) == brute_count_ge(values, v)

    # add / delete も含めて再検証
    S.delete(2)
    values.remove(2)
    S.add(6)
    values.append(6)
    assert len(S) == len(values)

    for v in range(-5, 15):
        assert S.count_less(v) == brute_count_less(values, v)
        assert S.count_ge(v) == brute_count_ge(values, v)
