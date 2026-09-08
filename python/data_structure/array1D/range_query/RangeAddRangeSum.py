# competitive-verifier: TITLE 区間加算・区間和 (Range Add Range Sum)

from python.data_structure.array1D.FenwickTree import FenwickTree

class RangeAddRangeSum():
    """半開区間への加算と区間和の取得を行う。"""
    def __init__(self, n, init=None):
        """n 要素の初期値列または零から区間加算・区間和用の木を構築する。"""
        if init is not None:
            init = list(init) + [0]
        self.bit0 = FenwickTree(n+1,init)
        self.bit1 = FenwickTree(n+1)

    def range_add(self,l,r,x):
        """半開区間 [l,r) の各要素に指定値を加える。"""
        self.bit0.add(l,-l*x)
        self.bit0.add(r,r*x)
        self.bit1.add(l,x)
        self.bit1.add(r,-x)

    # 半開区間 [0,r) 上の和
    def prefix_sum(self,r):
        """半開区間 [0,r) の要素和を返す。"""
        return self.bit1.prefix_sum(r)*r + self.bit0.prefix_sum(r)

    def range_sum(self,l,r):
        """半開区間 [l,r) の要素和を返す。"""
        return self.prefix_sum(r) - self.prefix_sum(l)
    
    def point_get(self,i):
        """指定した位置の値を返す。"""
        return self.range_sum(i,i+1)
