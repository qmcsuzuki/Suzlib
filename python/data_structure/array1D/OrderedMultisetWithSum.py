# competitive-verifier: TITLE 順序付き多重集合 + 和クエリ（値域が小さい）

from python.data_structure.array1D.FenwickTree import FenwickTree


class OrderedMultiset:
    def __init__(self, banhei_min, banhei_max):
        # 値域 (banhei_min, banhei_max) のみを扱う（両端は番兵）
        assert banhei_min + 1 <= banhei_max - 1
        self.banhei_min = banhei_min
        self.banhei_max = banhei_max
        self.cnt = -2  # 番兵を含めて add し、外部向けサイズは番兵を除く
        # 添字 (v - banhei_min) は [0, banhei_max-banhei_min] を取り得るため +1 が必要
        self.bit = FenwickTree(self.banhei_max - self.banhei_min + 1)  # 存在すれば 1、しないなら 0
        self.add(self.banhei_min)
        self.add(self.banhei_max)

    def __len__(self):
        return self.cnt

    def __contains__(self, v):
        i = v - self.banhei_min
        return self.bit.range_sum(i, i + 1) > 0

    def add(self, v, wt=1):  # 値 v を重み wt で追加（通常重み=1）
        self.cnt += wt
        self.bit.add(v - self.banhei_min, wt)

    def delete(self, v):  # 値 v を削除
        self.add(v, -1)

    def count_less(self, v):
        # v 未満の要素数（自動挿入される番兵 2 個は除く）
        min_val = self.banhei_min + 1
        if v <= min_val:
            return 0
        # v 未満の通常要素は [min_val, min(v,banhei_max))
        upper = min(v, self.banhei_max)
        return self.bit.prefix_sum(upper - self.banhei_min) - 1

    def count_eq(self, v):
        # ちょうど v の要素数
        if v <= self.banhei_min or v >= self.banhei_max:
            return 0
        i = v - self.banhei_min
        return self.bit.range_sum(i, i + 1)

    def count_ge(self, v):
        # v 以上の要素数（自動挿入される番兵 2 個は除く）
        return len(self) - self.count_less(v)

    def kth_value(self, k):
        # k 番目 (1-indexed) に小さい元の値を求める。k が大きすぎると、範囲外エラーとなるので注意
        return self.banhei_min + self.bit.bisect_left(k + 1)

    def kth_largest_value(self, k):
        # k 番目 (1-indexed) に大きい元の値を求める。k が大きすぎると、範囲外エラーとなるので注意
        return self.kth_value(len(self) - k + 1)

    def prev_value(self, v):  # 一個前の元の値
        s = self.bit.prefix_sum(v - self.banhei_min)
        return self.banhei_min + self.bit.bisect_left(s)

    def next_value(self, v):
        s = self.bit.prefix_sum(v - self.banhei_min + 1)
        return self.banhei_min + self.bit.bisect_left(s + 1)


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
