# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/range_affine_point_get

from python.data_structure.array1D.SegmentTreeDual import SegmentTreeDual

import sys
readline = sys.stdin.readline

MOD = 998244353
n,Q = map(int,readline().split())
*a, = map(int,readline().split())

"""
def op(f1,f2):
    a,b = f1
    c,d = f2
    return (a*c%MOD, (a*d+b)%MOD)

def mapping(f,x):
    return (f[0]*x+f[1])%MOD

seg = SegmentTreeDual(n, op, (1,0), is_commutative=False, init=None, mapping=mapping)
"""

MMM = 1<<31
def op(f1,f2):
    a,b = divmod(f1,MMM)
    c,d = divmod(f2,MMM)
    return encode(a*c%MOD, (a*d+b)%MOD)
    
def mapping(f,x):
    a,b = divmod(f,MMM)
    return (a*x+b)%MOD

def encode(a,b): return a*MMM + b

seg = SegmentTreeDual(n, op, encode(1,0), is_commutative=False, init=None, mapping=mapping)

for _ in range(Q):
    t,*lst = map(int,readline().split())

    if t == 0:
        l,r,b,c = lst
        seg.apply(l,r,encode(b,c))
    else:
        i = lst[0]
        b,c = divmod(seg.point_get(i),MMM)
        ans = (b*a[i]+c)%MOD
        assert ans == seg.apply_to_point(i,a[i])
        print(ans)
        #print(seg.apply_to_point(i,a[i]))







