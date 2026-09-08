# competitive-verifier: TITLE 区間反転・区間和（01列）

from python.data_structure.array1D.LazySegmentTree import LazySegmentTree

class RangeUpdateFlipRangeSum01:
    """
    01 列に対する range update / range xor (flip) / range sum

    - range_update(l, r, v): [l, r) をすべて v にする
    - range_flip(l, r):    [l, r) の各要素に ^= 1
    - range_sum(l, r):       [l, r) の 1 の個数

    内部では Suzlib の LazySegmentTree を使う。

    内部値は
        packed = one * BASE + length
    として整数 1 個で持つ。
    """

    ID = 0
    SET0 = 1
    SET1 = 2
    FLIP = 3

    def __init__(self, A):
        """0/1 列 A から区間更新・反転・和取得用の遅延セグメント木を構築する。"""
        self.N = len(A)
        self.BASE = self.N + 1

        def mapping(action, packed):
            """更新作用を区間の集約値に適用する。"""
            if action == RangeUpdateFlipRangeSum01.ID:
                return packed

            one, length = divmod(packed, self.BASE)

            if action == RangeUpdateFlipRangeSum01.SET0:
                return length

            if action == RangeUpdateFlipRangeSum01.SET1:
                return length * self.BASE + length

            # action == FLIP
            return (length - one) * self.BASE + length

        def compose(new_action, old_action):
            """
            new_action after old_action

            ID=0, SET0=1, SET1=2, FLIP=3 としているので、
            FLIP after old_action は old_action ^ 3 で書ける。
            """
            if new_action == RangeUpdateFlipRangeSum01.ID:
                return old_action
            if new_action < RangeUpdateFlipRangeSum01.FLIP:
                return new_action
            return old_action ^ RangeUpdateFlipRangeSum01.FLIP

        array = [a * self.BASE + 1 for a in A]

        self.seg = LazySegmentTree(
            int.__add__,
            0,
            mapping,
            compose,
            RangeUpdateFlipRangeSum01.ID,
            self.N,
            array,
        )

    def range_update(self, l, r, v):
        """半開区間 [l,r) の各要素を指定した 0 または 1 に置き換える。"""
        if v == 0:
            self.seg.apply(l, r, RangeUpdateFlipRangeSum01.SET0)
        else:
            self.seg.apply(l, r, RangeUpdateFlipRangeSum01.SET1)

    def range_flip(self, l, r):
        """半開区間 [l,r) の各要素の 0 と 1 を反転する。"""
        self.seg.apply(l, r, 3)

    def range_sum(self, l, r):
        """半開区間 [l,r) の要素和を返す。"""
        return self.seg.prod(l, r) // self.BASE

    def all_sum(self):
        """全要素の和を返す。"""
        return self.seg.all_prod() // self.BASE

    def point_get(self, p):
        """指定した位置の値を返す。"""
        return self.seg.point_get(p) // self.BASE
