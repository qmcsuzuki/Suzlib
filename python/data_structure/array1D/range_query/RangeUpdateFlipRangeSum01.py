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
        self.N = len(A)
        self.BASE = self.N + 1

        def mapping(action, packed):
            if action == RangeUpdateXorRangeSum01.ID:
                return packed

            one, length = divmod(packed, self.BASE)

            if action == RangeUpdateXorRangeSum01.SET0:
                return length

            if action == RangeUpdateXorRangeSum01.SET1:
                return length * self.BASE + length

            # action == FLIP
            return (length - one) * self.BASE + length

        def compose(new_action, old_action):
            """
            new_action after old_action

            ID=0, SET0=1, SET1=2, FLIP=3 としているので、
            FLIP after old_action は old_action ^ 3 で書ける。
            """
            if new_action == RangeUpdateXorRangeSum01.ID:
                return old_action
            if new_action < RangeUpdateXorRangeSum01.FLIP:
                return new_action
            return old_action ^ RangeUpdateXorRangeSum01.FLIP

        array = [a * self.BASE + 1 for a in A]

        self.seg = LazySegmentTree(
            int.__add__,
            0,
            mapping,
            compose,
            RangeUpdateXorRangeSum01.ID,
            self.N,
            array,
        )

    def range_update(self, l, r, v):
        if v == 0:
            self.seg.apply(l, r, RangeUpdateXorRangeSum01.SET0)
        else:
            self.seg.apply(l, r, RangeUpdateXorRangeSum01.SET1)

    def range_flip(self, l, r):
        self.seg.apply(l, r, 3)

    def range_sum(self, l, r):
        return self.seg.prod(l, r) // self.BASE

    def all_sum(self):
        return self.seg.all_prod() // self.BASE

    def point_get(self, p):
        return self.seg.point_get(p) // self.BASE
