class FenwickTreeDualGeneral2d:
    def __init__(self, h: int, w: int, op, e_M):
        self.h = h
        self.w = w
        self.op = op
        self.e_M = e_M
        self.data = [[e_M]*w for _ in range(h)]

    def prefix_add(self, r1, r2, x):
        """ 半閉区間 [0,r1) * [0,r2) 上に x を加算"""
        while r1 > 0:
            r = r2
            while r > 0:
                self.data[r1-1][r-1] = self.op(self.data[r1-1][r-1],x)
                r -= r & -r
            r1 -= r1 & -r1
        return

    def get(self, i, j) -> int:
        """ get a[i][j] """
        s = self.e_M
        i += 1
        while i <= self.h:
            jj = j+1
            while jj <= self.w:
                s = self.op(s,self.data[i-1][jj-1])
                jj += jj & -jj
            i += i & -i
        return s
