# competitive-verifier: STANDALONE

from random import Random

from python.matrix.GeneralMatrix import GeneralMatrix, TropicalMatrix
from python.matrix.ModMatrix import ModMatrixBase


class IntegerMatrix(GeneralMatrix):
    add = staticmethod(int.__add__)
    mul = staticmethod(int.__mul__)
    zero = 0
    one = 1


class Mat(ModMatrixBase):
    MOD = 101


def brute_mul(a, b, mod=None):
    result = [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
    return result if mod is None else [[x % mod for x in row] for row in result]


if __name__ == "__main__":
    rng = Random(8)
    for cls, mod in [(IntegerMatrix,None), (Mat,101)]:
        for n in range(1,5):
            for m in range(1,5):
                a = [[rng.randrange(10) for _ in range(m)] for _ in range(n)]
                b = [[rng.randrange(10) for _ in range(3)] for _ in range(m)]
                A, B = cls(n,m,a), cls(m,3,b)
                assert (A*B).matrix == brute_mul(a,b,mod)
                A *= B
                assert (A.n,A.m) == (n,3)
                assert A.matrix == brute_mul(a,b,mod)
                A[0,0] = 9
                assert A[0][0] == 9
                assert A.m == (A*cls.eye(3)).m
            a = [[rng.randrange(10) for _ in range(n)] for _ in range(n)]
            expected = cls.eye(n).matrix
            for k in range(6):
                assert (cls(n,n,a)**k).matrix == expected
                expected = brute_mul(expected,a,mod)
    A = Mat(2,2,[[1,2],[3,4]])
    assert A.times_const(-2).matrix == [[99,97],[95,93]]
    assert A.matrix == [[1,2],[3,4]]
    a = TropicalMatrix(1,2,[[3,7]])
    b = TropicalMatrix(1,2,[[5,2]])
    assert (a+b).matrix == [[3,2]]
    assert (TropicalMatrix(1,1,[[3]])**4).matrix == [[12]]
