# competitive-verifier: TITLE 区間加算・区間二乗和 mod 998244353

from python.data_structure.array1D.LazySegmentTree import LazySegmentTree
class RangeAddRangeSquareMOD(LazySegmentTree):
    """
    区間加算区間二乗和を MOD で計算する遅延セグ木
    (0乗,1乗,2乗) の和を持って計算
    """
    def __init__(self, N, array1D=None):
        """初期列の値・二乗・区間長を保持する遅延セグメント木を構築する。"""
        def op_X(X,Y):
            """左右の区間の集約値を合成する。"""
            return((X[0]+Y[0])%MOD, (X[1]+Y[1])%MOD, (X[2]+Y[2])%MOD)

        def mapping(v,X):
            """更新作用を区間の集約値に適用する。"""
            a,b,c = X
            return (a, (b+v*a)%MOD, (c+(2*b+v*a)%MOD*v)%MOD)

        super().__init__(op_X, (0,0,0), mapping, lambda v,w: (v+w)%MOD, 0, N, [(1,i,i*i%MOD) for i in array1D] if array1D is not None else [(1,0,0) for _ in range(N)])

# https://atcoder.jp/contests/abc455/submissions/75310937
