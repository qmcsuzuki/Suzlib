# competitive-verifier: TITLE 順序付き多重集合（値域が小さい）（ordered multiset, std::multiset）

from python.data_structure.array1D.FenwickTree import FenwickTree

class OrderedMultiset:
    def __init__(self, banhei_min, banhei_max):
        # 値域 (banhei_min, banhei_max) のみを扱う（両端は番兵）
        assert banhei_min + 1 <= banhei_max - 1
        self.banhei_min = banhei_min
        self.banhei_max = banhei_max
        # 添字 (v - banhei_min) は [0, banhei_max-banhei_min] を取り得るため +1 が必要
        self.bit = FenwickTree(self.banhei_max - self.banhei_min + 1) #存在すれば 1、しないなら 0
        self.add(self.banhei_min)
        self.add(self.banhei_max)

    def __contains__(self,v):
        i = v - self.banhei_min
        return self.bit.range_sum(i, i+1) > 0

    def add(self,v,wt=1): # 値 v を重み wt で追加（通常重み=1）
        self.bit.add(v - self.banhei_min, wt)
        
    def delete(self,v): # 値 v を削除
        self.add(v,-1)

    def count_less(self,v):
        # v 未満の要素数（自動挿入される番兵 2 個は除く）
        min_val = self.banhei_min + 1
        if v <= min_val:
            return 0
        # v 未満の通常要素は [min_val, min(v,banhei_max))
        upper = min(v, self.banhei_max)
        return self.bit.prefix_sum(upper - self.banhei_min) - 1

    def count_eq(self,v):
        # ちょうど v の要素数
        if v <= self.banhei_min or v >= self.banhei_max:
            return 0
        i = v - self.banhei_min
        return self.bit.range_sum(i, i+1)

    def count_ge(self,v):
        # v 以上の要素数（自動挿入される番兵 2 個は除く）
        max_val = self.banhei_max - 1
        if v > max_val:
            return 0
        lower = max(v, self.banhei_min + 1)
        return self.bit.suffix_sum(lower - self.banhei_min) - 1

    def kth_value(self,k):
        # k 番目 (1-indexed) に小さい元の値を求める。k が大きすぎると、範囲外エラーとなるので注意
        return self.banhei_min + self.bit.bisect_left(k+1)

    def kth_largest_value(self,k):
        # k 番目 (1-indexed) に大きい元の値を求める。k が大きすぎると、範囲外エラーとなるので注意
        size = self.bit.prefix_sum(self.bit.size) - 2
        return self.kth_value(size - k + 1)

    def prev_value(self,v): #一個前の元の値
        s = self.bit.prefix_sum(v - self.banhei_min)
        return self.banhei_min + self.bit.bisect_left(s)

    def next_value(self,v):
        s = self.bit.prefix_sum(v - self.banhei_min + 1)
        return self.banhei_min + self.bit.bisect_left(s+1)
