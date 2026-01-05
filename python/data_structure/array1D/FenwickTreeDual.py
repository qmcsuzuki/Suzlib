# competitive-verifier: TITLE Fenwick Tree Dual（区間加算・一点取得）

class FenwickTreeDual:
    def __init__(self, n: int, init=None):
        self.n = n
        if init is None:
            self.data = [0]*n
        else:
            self.data = data = list(init)
            assert n == len(data)
            for i in range(n):
                if (ii := i + ((i+1) & -(i+1))) < n:
                    data[i] -= data[ii]

    def prefix_add(self, r, x) -> None:
        """ 半閉区間 [0,r) 上に x を加算"""
        while r > 0:
            self.data[r-1] += x
            r -= r & -r
        return

    def suffix_add(self, l, x) -> None:
        """ 半閉区間 [l,\infty) 上に x を加算"""
        self.prefix_add(self.n,x)
        self.prefix_add(l,-x)

    def range_add(self, l, r, x):
        """ 半閉区間 [l,r) 上に x を加算"""
        self.prefix_add(r,x)
        self.prefix_add(l,-x)

    def point_get(self, i) -> int:
        """ return a[i] """
        s = 0
        i += 1
        while i <= self.n:
            s += self.data[i-1]
            i += i & -i
        return s
    
    def all_get(self):
        res = self.data[::]
        for i in range(self.n)[::-1]:
            if (ii := i + ((i+1) & -(i+1))) < self.n:
                res[i] += res[ii]
        return res            
