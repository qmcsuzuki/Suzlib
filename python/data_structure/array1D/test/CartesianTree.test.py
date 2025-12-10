# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/cartesian_tree

from python.data_structure.array1D.CartesianTree import Cartesian_tree_DFSsearch, Cartesian_tree_full, Cartesian_tree_simple

import sys
readline = sys.stdin.readline

n = int(readline())
*a, = map(int, readline().split())

p = P1 = Cartesian_tree_simple(a)
L,R,P2 = Cartesian_tree_full(a)
P3 = [0]*n
def calc(i,l,r,p): P3[i] = p
Cartesian_tree_full(a,calc)

assert P1 == P2 == P3
print(*[p if p != -1 else i for i, p in enumerate(parent)])
