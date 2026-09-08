# competitive-verifier: TITLE 絶対値関数の和 (AddAbsGetVal)

from python.data_structure.array1D.FenwickTree import FenwickTree
from bisect import bisect_left
class AddAbsGetValOffline:
    """折れ点の座標を事前に圧縮し、折れ線関数の加算と関数値の取得を行う。"""
    def __init__(self,sa,za):
        """整列済みの折れ点列 sa と圧縮表 za を使って零関数を初期化する。"""
        self.sa = sa
        self.za = za
        self.BIT_val = FenwickTree(len(sa) + 1)
        self.BIT_cnt = FenwickTree(len(sa) + 1)
        self.const = self.val_all = self.cnt_all = 0

    def add_abs(self,pos,a,b):
        """左側で a*(pos-x)、右側で b*(x-pos) となる折れ線関数を加える。"""
        idx = self.za[pos]
        self.BIT_val.add(idx, (a+b)*pos)
        self.BIT_cnt.add(idx, a+b)
        self.val_all += a*pos
        self.cnt_all += a

    def add_const(self,x):
        """現在の関数に定数を加える。"""
        self.const += x

    def getval(self, x, after_zaatu):
        """指定した点での関数値を返す。"""
        if after_zaatu:
            x,zx = self.sa[x],x
        else:
            zx = bisect_left(self.sa,x)
        val = self.BIT_val.prefix_sum(zx)
        cnt = self.BIT_cnt.prefix_sum(zx)
        return self.val_all - val - x*(self.cnt_all - cnt) + self.const

    def getmin(self):
        """現在の凸な折れ線関数の最小値を返す。"""
        idx = self.BIT_cnt.bisect_left(self.cnt_all)
        return self.getval(idx, True)
