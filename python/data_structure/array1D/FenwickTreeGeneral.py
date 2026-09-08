# competitive-verifier: TITLE 一般化Fenwick木 (Fenwick Tree General)

"""
一般の演算 op に関する Fenwick tree
あまり検証していない

- op は結合的かつ可換、e は単位元
- init は長さ n の初期値列。初期化は O(n)、更新・取得は O(log n)
- n=0 も可。空区間の取得結果は e（更新可能な添字はない）
- range_sum, suffix_sum を使う場合は逆演算 inv が必要
"""

class FenwickTreeGeneral:
    """可換モノイドの一点更新と区間集約を管理する Fenwick 木。"""
    def __init__(self, n, op, e, inv=None, init=None):
        """可換演算 op と単位元 e を設定し、n 要素の初期値を線形時間で構築する。"""
        assert n >= 0
        self.size = n
        self.longest_interval = 1<<(n.bit_length()-1) if n else 0
        self.e = e
        self.op = op
        self.inv = inv
        if init is None:
            self.data = [e]*n
        else:
            self.data = list(init)
            assert len(self.data) == n
            for i in range(n):
                i_above = i + ((i+1) & -(i+1))
                if i_above < n: self.data[i_above] = op(self.data[i_above], self.data[i])

    def prefix_sum(self, r):
        """ 半閉区間 [0,r) 上の和 a[0] op ... op a[r-1] を返す """
        s = self.e
        while r > 0:
            s = self.op(s,self.data[r-1])
            r -= r & -r
        return s

    def range_sum(self,l,r):
        """ 半閉区間 [l,r) 上の和 a[l] op ... op a[r-1] を返す """
        return self.op(self.prefix_sum(r), self.inv(self.prefix_sum(l)))

    def suffix_sum(self,l):
        """ l 以上の添字での和 a[l] op a[l+1] op ... + を返す """
        return self.op(self.prefix_sum(self.size), self.inv(self.prefix_sum(l)))

    def add(self, i, x):
        """ a[i] = a[i] op x """
        i += 1
        while i <= self.size:
            self.data[i-1] = self.op(self.data[i-1],x)
            i += i & -i
