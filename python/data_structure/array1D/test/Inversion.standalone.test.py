# competitive-verifier: STANDALONE

from random import shuffle

from python.data_structure.array1D.Inversion import (
    inversion,
    inversion_brute,
    inversion_general,
)


if __name__ == "__main__":
    for A in (
        [1, 2, 3, 4, 5, 6],
        [0, 1, 2, 3, 4, 5, 6],
        [2, 2, 5, 6, 6, 6],
        [0, 0, 2, 3, 3, 3, 6],
        [0],
        [1],
        [0, 0, 0, 1, 1, 1],
        [5, 5, 5, 6, 6, 6],
    ):
        for _ in range(100):
            shuffle(A)
            assert inversion_brute(A) == inversion(A) == inversion_general(A)
