class FenwickTree2d:
    def __init__(self, h: int, w: int, init=None):
        self.h = h
        self.w = w
        if init is None:
            self.data = [[0]*w for _ in range(h)]
        else:
            assert len(init) == h and len(init[0]) == w
            self.data = [list(row) for row in init]
            for i in range(h):
                for j in range(w):
                    if (j_above := j + ((j+1) & -(j+1))) < w:
                        self.data[i][j_above] += self.data[i][j]
            for i in range(h):
                if (i_above := i + ((i+1) & -(i+1))) < h:
                    for j in range(w):
                        self.data[i_above][j] += self.data[i][j]

    def prefix_sum(self, r1, r2):
        """ 半閉区間 [0,r1) * [0,r2) 上の和を返す """
        s = 0
        while r1 > 0:
            r = r2
            while r > 0:
                s += self.data[r1-1][r-1]
                r -= r & -r
            r1 -= r1 & -r1
        return s

    def range_sum(self,l1,r1,l2,r2):
        """ 半閉区間 [l1,r1)*[l2,r2) 上の和を返す """
        return self.prefix_sum(l1,l2) - self.prefix_sum(l1,r2) - self.prefix_sum(r1,l2) + self.prefix_sum(r1,r2) 

    def suffix_sum(self,l1,l2):
        """ 半閉区間 [l1,\infty)*[l2,\infty) 上の和を返す """
        return self.range_sum(l1, self.h, l2, self.w)
    
    def add(self, i, j, x):
        """ a[i][j] += x """
        i += 1
        while i <= self.h:
            jj = j+1
            while jj <= self.w:
                self.data[i-1][jj-1] += x
                jj += jj & -jj
            i += i & -i
