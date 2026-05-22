# competitive-verifier: STANDALONE

import python.matrix.FlattenMatrixFactory as FMF


def test_usual_matrix():
    op, E = FMF.make_usual_matrix(2)
    A = (1, 2,
         3, 4)
    B = (2, -1,
         0, 5)
    assert op(A, E) == A
    assert op(E, A) == A
    assert op(A, B) == (2, 9,
                        6, 17)


def test_modint_matrix():
    FMF.MOD = 13
    op, E = FMF.make_MODint_matrix(2)
    A = (12, 5,
         1, 9)
    B = (7, 11,
         6, 3)
    assert op(A, E) == tuple(x % 13 for x in A)
    assert op(E, B) == tuple(x % 13 for x in B)
    assert op(A, B) == (10, 4,
                        9, 12)


def test_minplus_maxplus():
    INF = 10**18
    op_min, E_min = FMF.make_minplus_matrix(2, INF)
    op_max, E_max = FMF.make_maxplus_matrix(2, -INF)

    A = (0, 4,
         INF, 1)
    B = (2, INF,
         3, 0)
    assert op_min(A, E_min) == A
    assert op_min(E_min, B) == B
    assert op_min(A, B) == (2, 4,
                            4, 1)

    C = (0, -3,
         -INF, 1)
    D = (2, -INF,
         -1, 0)
    assert op_max(C, E_max) == C
    assert op_max(E_max, D) == D
    assert op_max(C, D) == (2, -3,
                            0, 1)


def test_bool_maxmin_minmax():
    op_bool, E_bool = FMF.make_bool_matrix(3)
    A = (False, True, False,
         False, False, True,
         False, False, False)
    B = (False, False, True,
         True, False, False,
         False, True, False)
    assert op_bool(A, E_bool) == A
    assert op_bool(E_bool, B) == B
    assert op_bool(A, B) == (True, False, False,
                             False, True, False,
                             False, False, False)

    NEG_INF = -10**18
    INF = 10**18
    op_maxmin, E_maxmin = FMF.make_maxmin_matrix(2, NEG_INF, INF)
    X = (7, 2,
         NEG_INF, 5)
    Y = (3, NEG_INF,
         6, 1)
    assert op_maxmin(X, E_maxmin) == X
    assert op_maxmin(E_maxmin, Y) == Y
    assert op_maxmin(X, Y) == (3, 1,
                               5, 1)

    op_minmax, E_minmax = FMF.make_minmax_matrix(2, INF, NEG_INF)
    P = (4, 9,
         INF, 2)
    Q = (6, INF,
         1, 7)
    assert op_minmax(P, E_minmax) == P
    assert op_minmax(E_minmax, Q) == Q
    assert op_minmax(P, Q) == (6, 9,
                               2, 7)


def main():
    test_usual_matrix()
    test_modint_matrix()
    test_minplus_maxplus()
    test_bool_maxmin_minmax()


if __name__ == "__main__":
    main()
