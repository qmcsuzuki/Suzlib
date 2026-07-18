# competitive-verifier: STANDALONE

import random

from python.data_structure.array1D.CircularMultiset import (
    CircularMultisetLargeM,
    CircularMultisetSmallM,
)


def test(s, a, M):
    assert len(s) == len(a)
    for m in range(M):
        assert s.sum_right(m) == sum((x - m) % M for x in a)
        assert s.sum_left(m) == sum((m - x) % M for x in a)


if __name__ == "__main__":
    random.seed(0)
    for M in range(1, 20):
        initial = [random.randrange(M) for _ in range(20)]
        for cls in (CircularMultisetSmallM, CircularMultisetLargeM):
            a = initial[:]
            s = cls(M, a) if cls is CircularMultisetSmallM else cls(M, range(M), a)

            for _ in range(200):
                if not a or random.randrange(2) == 0:
                    x = random.randrange(M)
                    a.append(x)
                    s.add(x)
                else:
                    i = random.randrange(len(a))
                    x = a.pop(i)
                    s.delete(x)
                test(s, a, M)

    M = 10**18 + 3
    values = [0, 7, M - 1]
    a = [0, 7, M - 1, M - 1]
    s = CircularMultisetLargeM(M, values, a)
    for m in [0, 1, 8, M - 1]:
        assert s.sum_right(m) == sum((x - m) % M for x in a)
        assert s.sum_left(m) == sum((m - x) % M for x in a)
