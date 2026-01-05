# competitive-verifier: TITLE 行列（一般）

"""
演算が一般化された行列

遅かった（セグ木に載せるのは不可能）
演算は staticmethod にする必要がある
（下の TropicalMatrix の特殊化を参照のこと）
"""


class GeneralMatrix:
    add = None
    mul = None
    zero = None
    one = None
    def __init__(self, n: int, m: int, init=None, do_copy=True) -> None:
        self.n = n
        self.m = m
        if init is None:
            self.matrix = [[self.zero for _ in range(m)] for _ in range(n)]
        else:
            self.matrix = [row[:] for row in init] if do_copy else init
            assert n==len(self.matrix) and m == len(self.matrix[0])

    @classmethod
    def eye(cls, n: int):
        res = [[cls.one if i==j else cls.zero for i in range(n)] for j in range(n)]
        return cls(n,n,res,False)

    def __str__(self) -> str:
        return "\n".join(" ".join(map(str, row)) for row in self.matrix)

    def __getitem__(self, key) -> int:#: tuple[int, int]) -> int:
        return self.matrix[key]

    def __setitem__(self, indices) -> int: #: tuple[int, int], value: int) -> None:
        self.matrix[indices[0]][indices[1]] = value

    def __add__(self, other):
        assert self.n == other.n and self.m == other.m
        B,C = self.matrix, other.matrix
        res = [[(B[i][j] + C[i][j]) % self.MOD for j in range(self.m)] for i in range(self.n)]
        return self.__class__(self.n, self.m, res, False)

    def _matmul_list(self,B,C):
        A = [[self.zero]*len(C[0]) for _ in range(len(B))]
        for i,Ai in enumerate(A):
            for k,Bik in enumerate(B[i]):
                for j,Ckj in enumerate(C[k]):
                    Ai[j] = self.add(Ai[j], self.mul(Bik,Ckj))
        return A

    def __mul__(self, other):
        assert self.m == other.n
        res = self._matmul_list(self.matrix, other.matrix)
        return self.__class__(self.n, other.m, res, False)

    def __imul__(self, other):
        assert self.m == other.n
        self.matrix = self._matmul_list(self.matrix, other.matrix)
        return self

    def __pow__(self, k: int):
        res = [[self.one if i==j else self.zero for i in range(n)] for j in range(n)]
        tmp = self.matrix
        while k:
            if k & 1:
                res = self._matmul_list(res,tmp)
            tmp = self._matmul_list(tmp,tmp)
            k >>= 1
        return self.__class__(self.n, self.n, res, False)

INF = 1<<30
class TropicalMatrix(GeneralMatrix):
    add = staticmethod(lambda a, b: min(a, b))
    mul = staticmethod(lambda a, b: a + b)
    zero = INF
    one = 0
