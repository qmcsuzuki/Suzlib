# competitive-verifier: TITLE 順序付き多重集合 + 和クエリ（値域が小さい）

from python.data_structure.array1D.FenwickTree import FenwickTree
from python.data_structure.array1D.OrderedMultiset import OrderedMultiset


class OrderedMultisetWithSum(OrderedMultiset):
    def __init__(self, banhei_min, banhei_max):
        size = banhei_max - banhei_min + 1
        self.sum_bit = FenwickTree(size)
        # add で番兵も一様に加算するので、先に打ち消しておく
        self.total_sum = -banhei_min - banhei_max
        super().__init__(banhei_min, banhei_max)

    def add(self, v, wt=1):
        super().add(v, wt)
        self.sum_bit.add(v - self.banhei_min, v * wt)
        self.total_sum += v * wt

    def sum_less(self, v):
        # v 未満の要素和（自動挿入される番兵 2 個は除く）
        min_val = self.banhei_min + 1
        if v <= min_val:
            return 0
        upper = min(v, self.banhei_max)
        return self.sum_bit.prefix_sum(upper - self.banhei_min) - self.banhei_min

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

        # k 番目の通常要素値を求め、そこで分割して和を作る
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
