# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/point_set_range_composite

from python.data_structure.array1D.SegmentTree import SegmentTree
import sys
readline = sys.stdin.readline

MOD = 998244353

N, Q = map(int, readline().split())

res = []
for i in range(N):
    a, b = map(int, readline().split())
    res.append((a,b))

def op(f1,f2):
    a,b = f1
    c,d = f2
    return (a*c%MOD, (b*c+d)%MOD)

seg = SegmentTree(N,op,e=(1,0),init=res)

ans = []
for _ in range(Q):
    t, q, r, s = map(int, readline().split())
    if t==0:
        seg.update(q,(r,s))
    else:
        a,b = seg.prod(q,r)
        print((a*s+b)%MOD)

