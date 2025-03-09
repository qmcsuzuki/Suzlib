"""
S を常にソートされている配列（昇順・降順は事前に指定）として、
- sum((a*i+b)*v for i,v in enumerate(S)) を求める
    - つまり等差数列との内積を求める
- S に挿入
- S から削除（S に元があることを仮定）
"""
from FenwickTree import FenwickTree

class SortedArrayInnerProduct():
    def __init__(self,a,b,Maxvalue,reverse=0,init=None):
        self.fcnt = FenwickTree(Maxvalue+1)
        self.fsum = FenwickTree(Maxvalue+1)
        self.val = 0
        self.a = a
        self.b = b
        self.op_cnt = self.fcnt.prefix_sum if reverse==0 else self.fcnt.suffix_sum
        self.op_sum = self.fsum.suffix_sum if reverse==0 else self.fsum.prefix_sum
        
        if init:
            init = sorted(init,reverse=reverse)
            for x in init:
                self.insert(x)

    def insert(self,x):
        r1 = (self.op_cnt(x)*self.a + self.b)*x
        r2 = (self.op_sum(x)*self.a)
        self.val += r1+r2
        self.fcnt.add(x,1)
        self.fsum.add(x,x)

    def remove(self,x):
        self.fcnt.add(x,-1)
        self.fsum.add(x,-x)
        r1 = (self.op_cnt(x)*self.a + self.b)*x
        r2 = (self.op_sum(x)*self.a)
        self.val -= r1+r2
    
    def getvalue(self):
        return self.val

# https://atcoder.jp/contests/arc194/submissions/63609088
