# competitive-verifier: TITLE 行列（一般）

"""
演算が一般化された行列

遅かった（セグ木に載せるのは不可能）
演算は staticmethod にする必要がある
（下の TropicalMatrix の特殊化を参照のこと）
"""


class GeneralMatrix:
    """指定した加法・乗法による行列の演算と累乗を行う。"""
    add = None
    mul = None
    zero = None
    one = None
    def __init__(self, n: int, m: int, init=None, do_copy=True) -> None:
        """n 行 m 列の零行列または初期行列を、コピー指定に従って保持する。"""
        self.n = n
        self.m = m
        if init is None:
            self.matrix = [[self.zero for _ in range(m)] for _ in range(n)]
        else:
            self.matrix = [row[:] for row in init] if do_copy else init
            assert n==len(self.matrix) and m == len(self.matrix[0])

    @classmethod
    def eye(cls, n: int):
        """指定した次元の単位行列を生成して返す。"""
        res = [[cls.one if i==j else cls.zero for i in range(n)] for j in range(n)]
        return cls(n,n,res,False)

    def __str__(self) -> str:
        """現在の内容を表示用文字列に変換する。"""
        return "\n".join(" ".join(map(str, row)) for row in self.matrix)

    def __getitem__(self, key) -> int:#: tuple[int, int]) -> int:
        """指定した行番号またはスライスに対応する行を返す。"""
        return self.matrix[key]

    def __setitem__(self, indices, value) -> None:
        """添字の組 (i,j) に対応する行列成分を更新する。"""
        self.matrix[indices[0]][indices[1]] = value

    def __add__(self, other):
        """対応する成分を加えた新しい行列を返す。"""
        assert self.n == other.n and self.m == other.m
        B,C = self.matrix, other.matrix
        res = [[self.add(B[i][j], C[i][j]) for j in range(self.m)] for i in range(self.n)]
        return self.__class__(self.n, self.m, res, False)

    def _matmul_list(self,B,C):
        """行列積の成分を二次元リストで計算して返す。"""
        A = [[self.zero]*len(C[0]) for _ in range(len(B))]
        for i,Ai in enumerate(A):
            for k,Bik in enumerate(B[i]):
                for j,Ckj in enumerate(C[k]):
                    Ai[j] = self.add(Ai[j], self.mul(Bik,Ckj))
        return A

    def __mul__(self, other):
        """行列積を新しい行列として返す。"""
        assert self.m == other.n
        res = self._matmul_list(self.matrix, other.matrix)
        return self.__class__(self.n, other.m, res, False)

    def __imul__(self, other):
        """行列積で自身を更新して返す。"""
        assert self.m == other.n
        self.matrix = self._matmul_list(self.matrix, other.matrix)
        self.m = other.m
        return self

    def __pow__(self, k: int):
        """非負整数回の正方行列の累乗を二分累乗法で求める。"""
        n = self.n
        res = [[self.one if i==j else self.zero for i in range(n)] for j in range(n)]
        tmp = self.matrix
        while k:
            if k & 1:
                res = self._matmul_list(res,tmp)
            tmp = self._matmul_list(tmp,tmp)
            k >>= 1
        return self.__class__(self.n, self.n, res, False)

INF = 1<<60
class TropicalMatrix(GeneralMatrix):
    """最小値を加法、和を乗法とするトロピカル行列。"""
    add = staticmethod(lambda a, b: min(a, b))
    mul = staticmethod(lambda a, b: a + b)
    zero = INF
    one = 0
