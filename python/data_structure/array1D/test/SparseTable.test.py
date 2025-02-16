# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/staticrmq
# https://judge.yosupo.jp/submission/268030

from python.data_structure.array1D.SparseTable import SparseTable
import sys
readline = sys.stdin.readline

n,Q = map(int,readline().split())
*a, = map(int,readline().split())

def argmin(i,j):
    return i if a[i] <= a[j] else j

sp1 = SparseTable(a,min)
sp2 = SparseTable(list(range(n)),argmin)

for _ in range(Q):
    l,r = map(int,readline().split())
    print(v := sp1.prod(l,r))
    assert v == a[sp2.prod(l,r)]


