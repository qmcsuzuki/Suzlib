# competitive-verifier: TITLE 円周上の多重集合と距離和

"""
0, 1, ..., M-1 を円周状に並べた多重集合を管理する。

- CircularMultisetSmallM: M が小さい場合。O(M) memory
- CircularMultisetLargeM: M が大きい場合。追加され得る値の事前列挙が必要

各操作は Fenwick 木と二分探索により O(log M) または O(log K)。
"""

from bisect import bisect_left, bisect_right

from python.data_structure.array1D.FenwickTree import FenwickTree


class _CircularMultisetBase:
    def __init__(self, M, init):
        assert M > 0
        self.M = M
        self.cnt = 0
        self.total_sum = 0
        for x in init:
            self.add(x)

    def __len__(self):
        return self.cnt

    def add(self, x, wt=1):
        """値 x を wt 個追加する。"""
        assert 0 <= x < self.M
        self._add_count(x, wt)
        self.cnt += wt
        self.total_sum += x * wt

    def delete(self, x):
        """値 x を 1 個削除する。"""
        self.add(x, -1)

    def sum_right(self, m):
        """m から各 x への右回りの距離 (x-m) mod M の総和を返す。"""
        assert 0 <= m < self.M
        return self.total_sum - m * self.cnt + self.M * self._count_less(m)

    def sum_left(self, m):
        """m から各 x への左回りの距離 (m-x) mod M の総和を返す。"""
        assert 0 <= m < self.M
        return m * self.cnt - self.total_sum + self.M * self._count_greater(m)


class CircularMultisetSmallM(_CircularMultisetBase):
    """M が小さい場合の実装。使用メモリ O(M)、各操作 O(log M)。"""

    def __init__(self, M, init=()):
        self.cnt_bit = FenwickTree(M)
        super().__init__(M, init)

    def _add_count(self, x, wt):
        self.cnt_bit.add(x, wt)

    def _count_less(self, x):
        return self.cnt_bit.prefix_sum(x)

    def _count_greater(self, x):
        return self.cnt_bit.suffix_sum(x + 1)


class CircularMultisetLargeM(_CircularMultisetBase):
    """
    M が大きい場合の座標圧縮版。

    values には、初期値を含め今後追加され得る値をすべて渡す。
    K = len(set(values)) として、使用メモリ O(K)、各操作 O(log K)。
    """

    def __init__(self, M, values, init=()):
        self.values = sorted(set(values))
        assert all(0 <= x < M for x in self.values)
        self.cnt_bit = FenwickTree(max(1, len(self.values)))
        super().__init__(M, init)

    def _add_count(self, x, wt):
        i = bisect_left(self.values, x)
        assert i < len(self.values) and self.values[i] == x
        self.cnt_bit.add(i, wt)

    def _count_less(self, x):
        return self.cnt_bit.prefix_sum(bisect_left(self.values, x))

    def _count_greater(self, x):
        return self.cnt_bit.suffix_sum(bisect_right(self.values, x))
