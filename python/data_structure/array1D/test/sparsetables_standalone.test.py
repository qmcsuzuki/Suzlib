# competitive-verifier: STANDALONE

from python.data_structure.array1D.SparseTable import SparseTable
from python.data_structure.array1D.DisjointSparseTable import DisjointSparseTable

class SparseTableArgminmax(SparseTable):
    M = 1<<20
    def __init__(self, a, min_or_max):
        aa = [v*self.M+i for i,v in enumerate(a)]
        super().__init__(aa, min_or_max)
    
    """
    値、添え字のペアを返す
    """
    def prod(self, L,R):
        return divmod(super().prod(L,R),self.M)

from random import shuffle

def test_sparse_table(n):
    # test: 文字列結合 (非可換な場合)
    a = list(range(n))
    shuffle(a)
    sp = SparseTableArgminmax(a,min)
    for i in range(n):
        for j in range(i+1,n+1):
            val,idx = sp.prod(i,j)
            assert a[idx] == val == min(a[i:j])

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
    test_disjoint_sparse_table(n)
    test_sparse_table(n)
