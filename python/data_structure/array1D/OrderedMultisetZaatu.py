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
    """事前に列挙した値を座標圧縮して多重集合を管理する。"""
    def __init__(self, values, banhei_min, banhei_max):
        """候補値を座標圧縮し、上下の番兵だけを持つ多重集合を作る。"""
        values = sorted(set(values))
        assert banhei_min < banhei_max
        assert not values or banhei_min < values[0] <= values[-1] < banhei_max
        self.banhei_min = banhei_min
        self.banhei_max = banhei_max
        self.cnt = -2  # 番兵を含めて add し、外部向けサイズは番兵を除く
        self.sortedvalues = [banhei_min] + values + [banhei_max]
        self.za = {v:i for i,v in enumerate(self.sortedvalues)}
        self.bit = FenwickTree(len(self.sortedvalues)) #存在すれば 1、しないなら 0
        self.add(self.banhei_min)
        self.add(self.banhei_max)

    def __len__(self):
        """格納されている要素の個数を返す。"""
        return self.cnt

    def __contains__(self,v):
        """指定した値が格納されているかを返す。"""
        idx = self.za[v]
        return self.bit.range_sum(idx,idx+1) > 0

    def add(self,v,wt=1): # 値 v を重み wt で追加（通常重み=1）
        """登録済みの値 v の個数を wt だけ増減する。"""
        self.cnt += wt
        self.bit.add(self.za[v],wt)
        
    def delete(self,v): # 値を削除
        """存在する値 v を一つ削除する。"""
        self.add(v,-1)

    def count_less(self,v):
        """指定値未満の要素数を、自動挿入された番兵を除いて返す。"""
        # v 未満の要素数（自動挿入される番兵 2 個は除く）
        idx = bisect_left(self.sortedvalues, v)
        res = self.bit.prefix_sum(idx)
        if v > self.banhei_min:
            res -= 1
        if v > self.banhei_max:
            res -= 1
        return res

    def count_eq(self,v):
        """指定値と等しい要素数を、自動挿入された番兵を除いて返す。"""
        # ちょうど v の要素数（自動挿入される番兵は除く）
        if v <= self.banhei_min or v >= self.banhei_max or v not in self.za:
            return 0
        idx = self.za[v]
        return self.bit.range_sum(idx, idx+1)

    def count_ge(self,v):
        """指定値以上の要素数を、自動挿入された番兵を除いて返す。"""
        # v 以上の要素数（自動挿入される番兵 2 個は除く）
        idx = bisect_left(self.sortedvalues, v)
        res = self.bit.suffix_sum(idx)
        if v <= self.banhei_min:
            res -= 1
        if v <= self.banhei_max:
            res -= 1
        return res

    def kth_index(self,k): # k 番目 (1-indexed) に小さい元の sortedvalues における index
        """小さい方から 1-indexed で k 番目の要素の座標圧縮後の添字を返す。"""
        return self.bit.bisect_left(k+1)

    def kth_value(self,k):
        """小さい方から 1-indexed で k 番目の通常要素の値を返す。"""
        # k 番目に小さい元の値を求める。k が大きすぎると、範囲外エラーとなるので注意
        return self.sortedvalues[self.kth_index(k)]

    def kth_largest_value(self,k):
        """大きい方から 1-indexed で k 番目の通常要素の値を返す。"""
        # k 番目 (1-indexed) に大きい元の値を求める。k が大きすぎると、範囲外エラーとなるので注意
        size = self.bit.prefix_sum(self.bit.size)
        return self.kth_value(size - k - 1)

    def prev_index(self,v): #一個前の元の sortedvalues における index
        """指定値の直前の要素または下側の番兵の圧縮後の添字を返す。"""
        idx = bisect_left(self.sortedvalues,v)
        s = self.bit.prefix_sum(idx)
        assert s != 0
        idx = self.bit.bisect_left(s)
        return idx

    def prev_value(self,v): # v の一個前の元の値（なければ、番兵（小））
        """指定値より小さい最大の値を返し、なければ下側の番兵を返す。"""
        return self.sortedvalues[self.prev_index(v)]

    def next_index(self,v): #一個次の元の sortedvalues における index
        """英小文字列の各位置より後の次出現位置を 1-indexed で返し、未出現を -1 とする。"""
        idx = bisect_right(self.sortedvalues,v)
        s = self.bit.prefix_sum(idx)
        idx = self.bit.bisect_left(s+1)
        assert idx != self.bit.size
        return idx

    def next_value(self,v):# v の一個次の元の値（なければ、番兵（大））
        """指定値より大きい最小の値を返し、なければ上側の番兵を返す。"""
        return self.sortedvalues[self.next_index(v)]


class OrderedMultisetWithSumWithZaatu(OrderedMultisetWithZaatu):
    """座標圧縮した多重集合と順位・値域ごとの要素和を管理する。"""
    def __init__(self, values, banhei_min, banhei_max):
        """候補値を座標圧縮し、番兵付き多重集合と要素和の管理領域を作る。"""
        values = set(values)
        size = len(values) + 2
        self.sum_bit = FenwickTree(size)
        # add で番兵も一様に加算するので、先に打ち消しておく
        self.total_sum = -banhei_min - banhei_max
        super().__init__(values, banhei_min, banhei_max)

    def add(self, v, wt=1):
        """登録済みの値 v の個数を wt だけ増減し、要素和も更新する。"""
        super().add(v, wt)
        idx = self.za[v]
        self.sum_bit.add(idx, v * wt)
        self.total_sum += v * wt

    def sum_less(self, v):
        """指定値未満の要素和を、自動挿入された番兵を除いて返す。"""
        # v 未満の要素和（自動挿入される番兵 2 個は除く）
        idx = bisect_left(self.sortedvalues, v)
        res = self.sum_bit.prefix_sum(idx)
        if v > self.banhei_min:
            res -= self.banhei_min
        if v > self.banhei_max:
            res -= self.banhei_max
        return res

    def sum_ge(self, v):
        """指定値以上の要素和を、自動挿入された番兵を除いて返す。"""
        # v 以上の要素和（自動挿入される番兵 2 個は除く）
        return self.total_sum - self.sum_less(v)

    def sum_smallest_k(self, k):
        """小さい方から k 個の要素の和を返す。"""
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
        """大きい方から k 個の要素の和を返す。"""
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
        """指定値と等しい要素の和を、番兵を除いて返す。"""
        # ちょうど v の要素和
        if v == self.banhei_min or v == self.banhei_max:
            return 0
        return v * self.count_eq(v)

    def sum_range(self, l, r):
        """半開値域 [l,r) に含まれる要素の和を返す。"""
        # 半開区間 [l, r) の要素和
        if r <= l:
            return 0
        return self.sum_less(r) - self.sum_less(l)
