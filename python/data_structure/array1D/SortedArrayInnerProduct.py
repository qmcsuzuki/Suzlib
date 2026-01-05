# competitive-verifier: TITLE ソート列と等差数列の内積 (SortedArrayInnerProduct)

"""
S を常にソートされている配列（昇順・降順は事前に指定）として、
- sum((a*i+b)*v for i,v in enumerate(S)) を求める
    - つまり等差数列との内積を求める
- S に挿入
- S から削除（S に元があることを仮定）

座標圧縮をするなら za に圧縮を指定
"""
from FenwickTree import FenwickTree

class SortedArrayInnerProduct():
    def __init__(self,a,b,Maxvalue,reverse=0,za=None,init=None):
        self.fcnt = FenwickTree(Maxvalue+1)
        self.fsum = FenwickTree(Maxvalue+1)
        self.val = 0
        self.a = a
        self.b = b
        self.za = za
        self.op_cnt = self.fcnt.prefix_sum if reverse==0 else self.fcnt.suffix_sum
        self.op_sum = self.fsum.suffix_sum if reverse==0 else self.fsum.prefix_sum
        
        if init:
            init = sorted(init,reverse=reverse)
            if za is None:
                for x in init: self.insert(x)
            else:
                for x in init: self.insert_before_zaatu(x)

    def insert(self,x):
        assert self.za is None
        r1 = (self.op_cnt(x)*self.a + self.b)*x
        r2 = (self.op_sum(x)*self.a)
        self.val += r1+r2
        self.fcnt.add(x,1)
        self.fsum.add(x,x)

    def remove(self,x):
        assert self.za is None
        self.fcnt.add(x,-1)
        self.fsum.add(x,-x)
        r1 = (self.op_cnt(x)*self.a + self.b)*x
        r2 = (self.op_sum(x)*self.a)
        self.val -= r1+r2

    def insert_before_zaatu(self,x): # x は座標圧縮前
        idx = za[x]
        r1 = (self.op_cnt(idx)*self.a + self.b)*x
        r2 = (self.op_sum(idx)*self.a)
        self.val += r1+r2
        self.fcnt.add(idx,1)
        self.fsum.add(idx,x)

    def remove_before_zaatu(self,x): # x は座標圧縮前
        idx = za[x]
        self.fcnt.add(idx,-1)
        self.fsum.add(idx,-x)
        r1 = (self.op_cnt(idx)*self.a + self.b)*x
        r2 = (self.op_sum(idx)*self.a)
        self.val -= r1+r2
    
    def getvalue(self):
        return self.val

# https://atcoder.jp/contests/arc194/submissions/63610261
