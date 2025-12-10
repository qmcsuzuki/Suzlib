# competitive-verifier: STANDALONE

from python.data_structure.array1D.CartesianTree import Cartesian_tree_DFSsearch, Cartesian_tree_full

if __name__ == "__main__":
    for _ in range(1000):
        n = randrange(1,100)
        m = randrange(1,1000)
        A = [randrange(m) for _ in range(n)]

        L,R,P = Cartesian_tree_full(A)
        
        *LL, = *RR, = *PP, = [-1]*(n)
        def calc(i,l,r,p):
            LL[i],RR[i],PP[i] = l-1,r,p
        Cartesian_tree_DFSsearch(A)
        
        assert LL == L and RR == R and PP == P # check both give correct answer
        
        for i in range(n):
            l,r = L[i]+1, R[i]
            # 開区間 (l,r) で A[i] が最小、その両隣は A[l-1] < A[i] >= A[r] が成立（つまり同じ値は左から）
            assert (A[i]+1 if l+1 >= i else min(A[l:i])) > A[i] <= (A[i]+1 if i+1 >= r else min(A[i+1:r]))
            assert l == 0 or A[l-1] <= A[i]
            assert r == n or A[r] < A[i]
