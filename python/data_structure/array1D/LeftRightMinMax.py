# competitive-verifier: TITLE 左右累積 min/max


class LeftRightMinMax:
    """
    左右からの累積 min/max を前計算する。

    引数:
    - init: 元配列
    - min_or_max: min または max
    - e: 単位元。省略時は min なら +inf、max なら -inf

    返り値:
    - prefix_prod(r): min/max(a[:r])
    - suffix_prod(l): min/max(a[l:])

    計算量:
    - 構築 O(n)
    - 各クエリ O(1)

    不変条件:
    - left[i] = min/max(a[:i])
    - right[i] = min/max(a[i:])
    - 空区間は e を返す
    """
    def __init__(self, init, min_or_max=min, e=None):
        n = len(init)
        if e is None:
            if min_or_max is min:
                e = float("inf")
            elif min_or_max is max:
                e = -float("inf")
            else:
                raise ValueError("min/max 以外を使うときは e を与えてください")
        self.n = n
        self.op = min_or_max
        left = self.left = [e] * (n + 1)
        right = self.right = [e] * (n + 1)
        for i, x in enumerate(init):
            left[i + 1] = min_or_max(left[i], x)
        for i in range(n - 1, -1, -1):
            right[i] = min_or_max(init[i], right[i + 1])

    def prefix_prod(self, r):
        """半開区間 [0,r) の min/max を返す。"""
        assert 0 <= r <= self.n
        return self.left[r]

    def suffix_prod(self, l):
        """半開区間 [l,n) の min/max を返す。"""
        assert 0 <= l <= self.n
        return self.right[l]

    def minL(self, r):
        """prefix_prod の別名。min 用を想定。"""
        return self.prefix_prod(r)

    def minR(self, l):
        """suffix_prod の別名。min 用を想定。"""
        return self.suffix_prod(l)

    def maxL(self, r):
        """prefix_prod の別名。max 用を想定。"""
        return self.prefix_prod(r)

    def maxR(self, l):
        """suffix_prod の別名。max 用を想定。"""
        return self.suffix_prod(l)

    def all_prod(self):
        """配列全体の min/max を返す。"""
        return self.left[self.n]

    def prod_without(self, i):
        """a[i] を除いた min/max を返す。"""
        assert 0 <= i < self.n
        return self.op(self.left[i], self.right[i + 1])

    def prod_outside(self, l, r):
        """区間 [l,r) を除いた min/max を返す。"""
        assert 0 <= l <= r <= self.n
        return self.op(self.left[l], self.right[r])
