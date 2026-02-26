# competitive-verifier: TITLE 順序付き多重集合（値域が小さい）（ordered multiset, std::multiset）

from python.data_structure.array1D.FenwickTree import FenwickTree

class OrderedMultiset:
    def __init__(self, N, banhei): # 0 以上 N 以下
        # 番兵 -1 を FenwickTree の 0 として扱う、つまり外部の値 v では bit 内部の v+1 を操作することに注意
        assert banhei == N+1
        self.banhei_min = -1
        self.banhei_max = banhei
        self.bit = FenwickTree(N+3) #存在すれば 1、しないなら 0
        self.add(self.banhei_min)
        self.add(self.banhei_max)

    def __contains__(self,v):
        return self.bit.range_sum(v+1,v+2) > 0

    def add(self,v,wt=1): # 値 v を重み wt で追加（通常重み=1）
        self.bit.add(v+1,wt)
        
    def delete(self,v): # 値 v を削除
        self.add(v,-1)

    def count_less(self,v):
        # v 未満の要素数（自動挿入される番兵 2 個は除く）
        idx = max(0, min(self.bit.size, v+1))
        res = self.bit.prefix_sum(idx)
        if v > self.banhei_min:
            res -= 1
        if v > self.banhei_max:
            res -= 1
        return res

    def count_eq(self,v):
        # ちょうど v の要素数
        if v < self.banhei_min or v > self.banhei_max:
            return 0
        return self.bit.range_sum(v+1, v+2)

    def count_ge(self,v):
        # v 以上の要素数（自動挿入される番兵 2 個は除く）
        idx = max(0, min(self.bit.size, v+1))
        res = self.bit.suffix_sum(idx)
        if v <= self.banhei_min:
            res -= 1
        if v <= self.banhei_max:
            res -= 1
        return res

    def kth_value(self,k):
        # k 番目 (1-indexed) に小さい元の値を求める。k が大きすぎると、範囲外エラーとなるので注意
        return self.bit.bisect_left(k+1) - 1

    def kth_largest_value(self,k):
        # k 番目 (1-indexed) に大きい元の値を求める。k が大きすぎると、範囲外エラーとなるので注意
        size = self.bit.prefix_sum(self.bit.size)
        return self.kth_value(size - k - 1)

    def prev_value(self,v): #一個前の元の値
        s = self.bit.prefix_sum(v+1)
        return self.bit.bisect_left(s) - 1

    def next_value(self,v):
        s = self.bit.prefix_sum(v+2)
        return self.bit.bisect_left(s+1) - 1
