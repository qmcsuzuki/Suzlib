# competitive-verifier: TITLE 絶対値関数の和 (AddAbsGetVal)

from bisect import bisect_left
class AddAbsGetValOffline:
    def __init__(self,sa,za):
        self.sa = sa
        self.za = za
        self.BIT_val = FenwickTree(len(sa) + 1)
        self.BIT_cnt = FenwickTree(len(sa) + 1)
        self.const = self.val_all = self.cnt_all = 0

    def add_abs(self,pos,a,b):
        idx = self.za[pos]
        self.BIT_val.add(idx, (a+b)*pos)
        self.BIT_cnt.add(idx, a+b)
        self.val_all += a*pos
        self.cnt_all += a

    def add_const(self,x):
        self.const += x

    def getval(self, x, after_zaatu):
        if after_zaatu:
            x,zx = self.sa[x],x
        else:
            zx = bisect_left(self.sa,x)
        val = self.BIT_val.prefix_sum(zx)
        cnt = self.BIT_cnt.prefix_sum(zx)
        return self.val_all - val - x*(self.cnt_all - cnt) + self.const

    def getmin(self):
        idx = self.BIT_cnt.bisect_left(self.cnt_all)
        return self.getval(idx, True)
