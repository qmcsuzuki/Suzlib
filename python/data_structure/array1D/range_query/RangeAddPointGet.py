# competitive-verifier: TITLE 区間加算・一点取得

from python.data_structure.array1D.FenwickTree import FenwickTree

class RangeAddPointGet(FenwickTree):
    """半開区間への加算と一点取得を行う。"""
    def __init__(self, n, init=None):
        """n 要素の初期値列または零から区間加算用の Fenwick 木を構築する。"""
        if init is not None:
            init = list(init) + [0]
            for i in range(1,n)[::-1]:
                init[i] -= init[i-1]
        super().__init__(n+1,init)
        
    def range_add(self,l,r,x):
        """半開区間 [l,r) の各要素に指定値を加える。"""
        self.add(l,x)        
        self.add(r,-x)
    
    def point_get(self,i):
        """指定した位置の値を返す。"""
        return self.prefix_sum(i+1)

    def all_get(self):
        """内部の Fenwick 木から全位置の値を復元したリストを返す。"""
        data = self.data[:-1]
        for i in range(1,len(data)):
            ii = i - ((i+1) & -(i+1))
            if ii >= 0:
                data[i] += data[ii]
        return data
