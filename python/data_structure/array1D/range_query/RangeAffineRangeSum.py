# competitive-verifier: TITLE 区間アフィン変換・区間和 mod 998244353

from python.data_structure.array1D.LazySegmentTree import LazySegmentTree

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
        """n 要素の初期列または零を、区間長付きの内部表現で構築する。"""
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
        """左右の区間の集約値を合成する。"""
        Z = X + Y
        return Z if Z < self.MASK_FIRST else Z - self.MASK_FIRST

    def mapping(self, F, X):
        """更新作用を区間の集約値に適用する。"""
        x = X >> self.SHIFT
        v = X & self.MASK
        a = F >> self.SHIFT
        b = F & self.MASK
        return (((x*a + v*b) % self.MOD) << self.SHIFT) + v

    def compose(self, G, F):
        """二つの更新作用を適用順に従って合成する。"""
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
        """要素の値を、区間長を持つ内部表現に符号化する。"""
        return ((x % self.MOD) << self.SHIFT) + 1

    def pack_action(self, a, b):
        """アフィン変換の係数を内部表現に符号化する。"""
        return ((a % self.MOD) << self.SHIFT) + (b % self.MOD)

    def range_affine(self, l, r, a, b):
        """半開区間 [l,r) にアフィン変換 x -> a*x+b を適用する。"""
        self.apply(l, r, self.pack_action(a, b))

    def range_add(self, l, r, x):
        """半開区間 [l,r) の各要素に指定値を加える。"""
        self.apply(l, r, self.id_of_Aut_X + (x % self.MOD))

    def range_mul(self, l, r, x):
        """半開区間 [l,r) の各要素を指定値倍する。"""
        self.apply(l, r, (x % self.MOD) << self.SHIFT)

    def range_set(self, l, r, x):
        """半開区間 [l,r) の各要素を指定値に置き換える。"""
        self.apply(l, r, x % self.MOD)

    def range_sum(self, l, r):
        """半開区間 [l,r) の要素和を返す。"""
        return self.prod(l, r) >> self.SHIFT

    def all_sum(self):
        """全要素の和を返す。"""
        return self.all_prod() >> self.SHIFT

    def point_get(self, p):
        """指定した位置の値を返す。"""
        return super().point_get(p) >> self.SHIFT

    def point_set(self, p, x):
        """指定した位置の値を上書きする。"""
        super().point_set(p, self.pack_value(x))

    def point_apply(self, p, a, b):
        """指定した一点にアフィン変換を適用する。"""
        self.apply_point(p, self.pack_action(a, b))

    def __getitem__(self, p):
        """指定した添字またはキーに対応する値を返す。"""
        return self.point_get(p)
