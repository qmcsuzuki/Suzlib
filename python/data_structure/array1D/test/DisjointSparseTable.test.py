# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/staticrmq
# https://judge.yosupo.jp/submission/268038

from python.data_structure.array1D.SparseTable import DisjointSparseTable
import sys
readline = sys.stdin.readline

n,Q = map(int,readline().split())
*a, = map(int,readline().split())

sp = DisjointSparseTable(a,min)

for _ in range(Q):
    l,r = map(int,readline().split())
    print(sp.prod(l,r))
