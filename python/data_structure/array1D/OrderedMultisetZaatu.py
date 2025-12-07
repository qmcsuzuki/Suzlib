"""
座標圧縮+ BIT の ordered set もどき
番兵は自分で挿入すること
引数: 
- values: 集合に入りうる値をクエリ先読み
提出例: https://atcoder.jp/contests/abc430/submissions/70631379
"""

from bisect import bisect_left, bisect_right
class OrderedMultisetWithZaatu:
    def __init__(self, values):
        self.sortedvalues = sorted(set(values))
        self.za = {v:i for i,v in enumerate(self.sortedvalues)}
        self.bit = FenwickTree(len(self.sortedvalues)) #存在すれば 1、しないなら 0

    def __contains__(self,v):
        idx = self.za[v]
        return self.bit.range_sum(idx,idx+1) > 0

    def add(self,v,wt=1): # 値 v を重み wt で追加（通常重み=1）
        self.bit.add(self.za[v],wt)
        
    def delete(self,v): # 値を削除
        self.add(v,-1)

    def kth_index(self,k): # k 番目 (1-indexed) に小さい元の sortedvalues における index
        return self.bit.bisect_left(k)

    def kth_value(self,k):
        # k 番目に小さい元の値を求める。k が大きすぎると、範囲外エラーとなるので注意
        return self.sortedvalues[self.kth_index(k)]

    def prev_index(self,v): #一個前の元の sortedvalues における index
        idx = bisect_left(self.sortedvalues,v)
        s = self.bit.prefix_sum(idx)
        assert s != 0
        idx = self.bit.bisect_left(s)
        return idx

    def prev_value(self,v):
        return self.sortedvalues[self.prev_index(v)]

    def next_index(self,v): #次の元の sortedvalues における index
        idx = bisect_right(self.sortedvalues,v)
        s = self.bit.prefix_sum(idx)
        idx = self.bit.bisect_left(s+1)
        assert idx != self.bit.size
        return idx

    def next_value(self,v):
        return self.sortedvalues[self.next_index(v)]
