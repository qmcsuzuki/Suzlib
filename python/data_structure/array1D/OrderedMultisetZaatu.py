# competitive-verifier: TITLE 順序付き多重集合 with 座標圧縮（ordered multiset with zaatu）


"""
座標圧縮+ BIT の ordered multiset もどき
番兵は、勝手に集合に挿入される
引数: 
- values: 集合に入りうる値をクエリ先読み
- banhei_min: 番兵（全ての values より小さい値）
- banhei_max: 番兵（全ての values より大きい値）
提出例:
- https://atcoder.jp/contests/abc430/submissions/70631379
- https://judge.yosupo.jp/submission/335160
"""
from python.data_structure.array1D.FenwickTree import FenwickTree

from bisect import bisect_left, bisect_right
class OrderedMultisetWithZaatu:
    def __init__(self, values, banhei_min, banhei_max):
        assert banhei_min < min(values) and max(values) < banhei_max
        self.banhei_min = banhei_min
        self.banhei_max = banhei_max
        self.cnt = -2  # 番兵を含めて add し、外部向けサイズは番兵を除く
        self.sortedvalues = [banhei_min] + sorted(set(values)) + [banhei_max]
        self.za = {v:i for i,v in enumerate(self.sortedvalues)}
        self.bit = FenwickTree(len(self.sortedvalues)) #存在すれば 1、しないなら 0
        self.add(self.banhei_min)
        self.add(self.banhei_max)

    def __len__(self):
        return self.cnt

    def __contains__(self,v):
        idx = self.za[v]
        return self.bit.range_sum(idx,idx+1) > 0

    def add(self,v,wt=1): # 値 v を重み wt で追加（通常重み=1）
        self.cnt += wt
        self.bit.add(self.za[v],wt)
        
    def delete(self,v): # 値を削除
        self.add(v,-1)

    def count_less(self,v):
        # v 未満の要素数（自動挿入される番兵 2 個は除く）
        idx = bisect_left(self.sortedvalues, v)
        res = self.bit.prefix_sum(idx)
        if v > self.banhei_min:
            res -= 1
        if v > self.banhei_max:
            res -= 1
        return res

    def count_eq(self,v):
        # ちょうど v の要素数
        if v not in self.za:
            return 0
        idx = self.za[v]
        return self.bit.range_sum(idx, idx+1)

    def count_ge(self,v):
        # v 以上の要素数（自動挿入される番兵 2 個は除く）
        idx = bisect_left(self.sortedvalues, v)
        res = self.bit.suffix_sum(idx)
        if v <= self.banhei_min:
            res -= 1
        if v <= self.banhei_max:
            res -= 1
        return res

    def kth_index(self,k): # k 番目 (1-indexed) に小さい元の sortedvalues における index
        return self.bit.bisect_left(k+1)

    def kth_value(self,k):
        # k 番目に小さい元の値を求める。k が大きすぎると、範囲外エラーとなるので注意
        return self.sortedvalues[self.kth_index(k)]

    def kth_largest_value(self,k):
        # k 番目 (1-indexed) に大きい元の値を求める。k が大きすぎると、範囲外エラーとなるので注意
        size = self.bit.prefix_sum(self.bit.size)
        return self.kth_value(size - k - 1)

    def prev_index(self,v): #一個前の元の sortedvalues における index
        idx = bisect_left(self.sortedvalues,v)
        s = self.bit.prefix_sum(idx)
        assert s != 0
        idx = self.bit.bisect_left(s)
        return idx

    def prev_value(self,v): # v の一個前の元の値（なければ、番兵（小））
        return self.sortedvalues[self.prev_index(v)]

    def next_index(self,v): #一個次の元の sortedvalues における index
        idx = bisect_right(self.sortedvalues,v)
        s = self.bit.prefix_sum(idx)
        idx = self.bit.bisect_left(s+1)
        assert idx != self.bit.size
        return idx

    def next_value(self,v):# v の一個次の元の値（なければ、番兵（大））
        return self.sortedvalues[self.next_index(v)]


class OrderedMultisetWithSumWithZaatu(OrderedMultisetWithZaatu):
    def __init__(self, values, banhei_min, banhei_max):
        size = len(set(values)) + 2
        self.sum_bit = FenwickTree(size)
        # add で番兵も一様に加算するので、先に打ち消しておく
        self.total_sum = -banhei_min - banhei_max
        super().__init__(values, banhei_min, banhei_max)

    def add(self, v, wt=1):
        super().add(v, wt)
        idx = self.za[v]
        self.sum_bit.add(idx, v * wt)
        self.total_sum += v * wt

    def sum_less(self, v):
        # v 未満の要素和（自動挿入される番兵 2 個は除く）
        idx = bisect_left(self.sortedvalues, v)
        res = self.sum_bit.prefix_sum(idx)
        if v > self.banhei_min:
            res -= self.banhei_min
        if v > self.banhei_max:
            res -= self.banhei_max
        return res

    def sum_ge(self, v):
        # v 以上の要素和（自動挿入される番兵 2 個は除く）
        return self.total_sum - self.sum_less(v)

    def sum_smallest_k(self, k):
        # k > len(self) は len(self) に丸める（Python の slicing 互換）
        assert 0 <= k
        n = len(self)
        k = min(k, n)
        if k == 0:
            return 0
        if k == n:
            return self.total_sum

        v = self.kth_value(k)
        cnt_before = self.count_less(v)
        need = k - cnt_before
        return self.sum_less(v) + v * need

    def sum_top_k(self, k):
        # 大きい方から k 個の要素和（k > len(self) は len(self) に丸める）
        assert 0 <= k
        if k == 0:
            return 0
        n = len(self)
        k = min(k, n)
        if k == n:
            return self.total_sum
        return self.total_sum - self.sum_smallest_k(n - k)

    def sum_eq(self, v):
        # ちょうど v の要素和
        return v * self.count_eq(v)

    def sum_range(self, l, r):
        # 半開区間 [l, r) の要素和
        if r <= l:
            return 0
        return self.sum_less(r) - self.sum_less(l)
