# competitive-verifier: TITLE 区間アフィン変換・区間和 mod 998244353

from data_structure.array1D.LazySegmentTree import LazySegmentTree

class RangeAffineRangeSumMOD998244353(LazySegmentTree):
    """
    mod 998244353 の区間アフィン変換・区間和
    内部表現:
        X = (sum << 32) + length
        F = (a << 32) + b
    """

    MOD = 998244353
    SHIFT = 32
    MMM = 1 << SHIFT
    MASK = MMM - 1
    MASK_FIRST = MOD << SHIFT

    e_X = 0
    id_of_Aut_X = 1 << SHIFT

    def __init__(self, n, array=None):
        if array is None:
            array = [1] * n
        else:
            assert len(array) == n
            array = [self.pack_value(x) for x in array]

        super().__init__(
            self.op_X,
            self.e_X,
            self.mapping,
            self.compose,
            self.id_of_Aut_X,
            n,
            array,
        )

    def op_X(self, X, Y):
        Z = X + Y
        return Z if Z < self.MASK_FIRST else Z - self.MASK_FIRST

    def mapping(self, F, X):
        x = X >> self.SHIFT
        v = X & self.MASK
        a = F >> self.SHIFT
        b = F & self.MASK
        return (((x*a + v*b) % self.MOD) << self.SHIFT) + v

    def compose(self, G, F):
        # G after F
        # F(x) = a*x + b
        # G(x) = c*x + d
        # G(F(x)) = c*a*x + c*b + d
        a = F >> self.SHIFT
        b = F & self.MASK
        c = G >> self.SHIFT
        d = G & self.MASK
        return ((a*c % self.MOD) << self.SHIFT) + (c*b + d) % self.MOD

    def pack_value(self, x):
        return ((x % self.MOD) << self.SHIFT) + 1

    def pack_action(self, a, b):
        return ((a % self.MOD) << self.SHIFT) + (b % self.MOD)

    def range_affine(self, l, r, a, b):
        self.apply(l, r, self.pack_action(a, b))

    def range_add(self, l, r, x):
        self.apply(l, r, self.id_of_Aut_X + (x % self.MOD))

    def range_mul(self, l, r, x):
        self.apply(l, r, (x % self.MOD) << self.SHIFT)

    def range_set(self, l, r, x):
        self.apply(l, r, x % self.MOD)

    def range_sum(self, l, r):
        return self.prod(l, r) >> self.SHIFT

    def all_sum(self):
        return self.all_prod() >> self.SHIFT

    def point_get(self, p):
        return super().point_get(p) >> self.SHIFT

    def point_set(self, p, x):
        super().point_set(p, self.pack_value(x))

    def point_apply(self, p, a, b):
        self.apply_point(p, self.pack_action(a, b))

    def __getitem__(self, p):
        return self.point_get(p)
