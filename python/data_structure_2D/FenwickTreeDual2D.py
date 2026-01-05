# verification-helper: TITLE 2次元Fenwick Tree Dual

class FenwickTreeDual2D:
    def __init__(self, h: int, w: int):
        self.h = h
        self.w = w
        self.data = [[0]*w for _ in range(h)]

    def prefix_add(self, r1, r2, x) -> None:
        """ 半閉区間 [0,r1) * [0,r2) 上に x を加算"""
        while r1 > 0:
            r = r2
            while r > 0:
                self.data[r1-1][r-1] += x
                r -= r & -r
            r1 -= r1 & -r1
        return

    def get(self, i, j) -> int:
        """ get a[i][j] """
        s = 0
        i += 1
        while i <= self.h:
            jj = j+1
            while jj <= self.w:
                s += self.data[i-1][jj-1]
                jj += jj & -jj
            i += i & -i
        return s
