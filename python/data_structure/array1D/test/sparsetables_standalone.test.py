# competitive-verifier: STANDALONE

from python.data_structure.array1D.SparseTable import SparseTable, SparseTableArgminmax
from python.data_structure.array1D.DisjointSparseTable import DisjointSparseTable


from random import shuffle

def test_sparse_table(n):
    a = list(range(n))
    shuffle(a)
    # test 1: argmin
    # test2: x*y = x (非可換な場合)
    sp1 = SparseTableArgminmax(a,min)
    sp2 = SparseTable(a,lambda x,y: x)
    for i in range(n):
        for j in range(i+1,n+1):
            val,idx = sp1.prod(i,j)
            assert a[idx] == val == min(a[i:j])
            r = sp2.prod(i,j)
            assert r == a[i]

def test_disjoint_sparse_table(n):
    # test: 文字列結合 (非可換な場合)
    a = list(range(n))
    shuffle(a)
    s = list(map(str,a)) # ランダム数字列
    sp = DisjointSparseTable(s,lambda x,y: x+y)
    for i in range(n):
        for j in range(i+1,n+1):
            r = sp.prod(i,j)
            assert r == "".join(s[i:j])

for n in range(1,35):
    for T in range(10):
        test_disjoint_sparse_table(n)
        test_sparse_table(n)
