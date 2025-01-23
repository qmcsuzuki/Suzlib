class ModMatrixBase:
    def __init__(self, n: int, m: int, init=None, do_copy=True) -> None:
        self.n = n
        self.m = m
        if init is None:
            self.matrix = [[0]*m for _ in range(n)]
        else:
            self.matrix = [row[:] for row in init] if do_copy else init
            assert n==len(self.matrix) and m == len(self.matrix[0])

    @classmethod
    def eye(cls, n: int):
        res = [[int(i==j) for i in range(n)] for j in range(n)]
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

    def __pos__(self):
        return self

    def __neg__(self):
        B = self.matrix
        res = [[-B[i][j] % self.MOD for j in range(self.m)] for i in range(self.n)]
        return self.__class__(self.n, self.m, res, False)

    def __sub__(self, other):
        assert self.n == other.n and self.m == other.m
        B,C = self.matrix, other.matrix
        res = [[(B[i][j] - C[i][j]) % self.MOD for j in range(self.m)] for i in range(self.n)]
        return self.__class__(self.n, self.m, res, False)
    
    def _matmul_list(self,B,C):
        A = [[0]*len(C[0]) for _ in range(len(B))]
        for i,Ai in enumerate(A):
            for k,Bik in enumerate(B[i]):
                for j,Ckj in enumerate(C[k]):
                    Ai[j] = (Ai[j] + Bik * Ckj) % self.MOD
        return A

    def __mul__(self, other):
        assert self.m == other.n
        res = self._matmul_list(self.matrix, other.matrix)
        return self.__class__(self.n, other.m, res, False)

    def __imul__(self, other):
        assert self.m == other.n
        self.matrix = self._matmul_list(self.matrix, other.matrix)
        return self

    def times_const(self, k: int):
        res = self.__class__(self.n, other.m)
        A = res.matrix
        for i,Ai in enumerate(A):
            for j in range(self.m):
                Ai[j] = Ai[j] * k % self.MOD
        return res

    def __pow__(self, k: int):
        res = [[int(i==j) for i in range(self.n)] for j in range(self.n)]
        tmp = self.matrix
        while k:
            if k & 1:
                res = self._matmul_list(res,tmp)
            tmp = self._matmul_list(tmp,tmp)
            k >>= 1
        return self.__class__(self.n, self.n, res, False)

