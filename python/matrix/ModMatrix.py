# competitive-verifier: TITLE mod M の行列

"""
modint を成分に持つ行列の基底クラス

class Mat(ModMatrixBase):
    MOD = 998244353

のように、クラス変数 MOD を指定して使う
"""
class ModMatrixBase:
    """法 MOD による行列の加減算・乗算と累乗を行う基底クラス。"""
    def __init__(self, n: int, m: int, init=None, do_copy=True) -> None:
        """n 行 m 列の零行列または初期行列を、コピー指定に従って保持する。"""
        self.n = n
        self.m = m
        if init is None:
            self.matrix = [[0]*m for _ in range(n)]
        else:
            self.matrix = [row[:] for row in init] if do_copy else init
            assert n==len(self.matrix) and m == len(self.matrix[0])

    @classmethod
    def eye(cls, n: int):
        """指定した次元の単位行列を生成して返す。"""
        res = [[int(i==j) for i in range(n)] for j in range(n)]
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
        res = [[(B[i][j] + C[i][j]) % self.MOD for j in range(self.m)] for i in range(self.n)]
        return self.__class__(self.n, self.m, res, False)

    def __pos__(self):
        """単項プラスとして自身をそのまま返す。"""
        return self

    def __neg__(self):
        """各成分の加法逆元を持つ新しい行列を返す。"""
        B = self.matrix
        res = [[(self.MOD-Bi[j] if Bi[j] != 0 else 0) for j in range(self.m)] for Bi in self.matrix]
        return self.__class__(self.n, self.m, res, False)

    def __sub__(self, other):
        """対応する成分を引いた新しい行列を返す。"""
        assert self.n == other.n and self.m == other.m
        B,C = self.matrix, other.matrix
        res = [[(B[i][j] - C[i][j]) % self.MOD for j in range(self.m)] for i in range(self.n)]
        return self.__class__(self.n, self.m, res, False)
    
    def _matmul_list(self,B,C):
        """行列積の成分を二次元リストで計算して返す。"""
        A = [[0]*len(C[0]) for _ in range(len(B))]
        for i,Ai in enumerate(A):
            for k,Bik in enumerate(B[i]):
                for j,Ckj in enumerate(C[k]):
                    Ai[j] = (Ai[j] + Bik * Ckj) % self.MOD
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

    def times_const(self, k: int):
        """全成分を定数倍した新しい行列を返す。"""
        res = self.__class__(self.n, self.m)
        A = res.matrix
        for i,Ai in enumerate(A):
            for j in range(self.m):
                Ai[j] = self.matrix[i][j] * k % self.MOD
        return res

    def __pow__(self, k: int):
        """非負整数回の正方行列の累乗を二分累乗法で求める。"""
        res = [[int(i==j) for i in range(self.n)] for j in range(self.n)]
        tmp = self.matrix
        while k:
            if k & 1:
                res = self._matmul_list(res,tmp)
            tmp = self._matmul_list(tmp,tmp)
            k >>= 1
        return self.__class__(self.n, self.n, res, False)

