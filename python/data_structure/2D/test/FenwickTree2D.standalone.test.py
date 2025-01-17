# competitive-verifier: STANDALONE

from python.data_structure.2D.FenwickTree2D import FenwickTree2D
from python.data_structure.2D.FenwickTreeDual2D import FenwickTreeDual2D
from python.data_structure.2D.FenwickTreeDualGeneral2D import FenwickTreeDualGeneral2D

if __name__ == "__main__":
    from itertools import product
    # test FenwickTree2d
    for m,n in product(range(1,10),range(1,10)):
        for init in [None, [[i*j+1 for j in range(m)] for i in range(n)]]:
            bit = FenwickTree2d(n,m,init)
            if init == None: init = [[0]*m for _ in range(n)]
            
            for i,j in product(range(n),range(m)):
                bit.add(i,j,d:=i-j)
                init[i][j] += d
            
            # check range query
            for r1,r2 in product(range(n+1),range(m+1)):
                assert sum(sum(init[x][:r2]) for x in range(r1)) == bit.prefix_sum(r1,r2)
                assert sum(sum(init[x][r2:]) for x in range(r1,n)) == bit.suffix_sum(r1,r2)
                
                for l1,l2 in product(range(r1+1),range(r2+1)):
                    assert sum(sum(init[x][l2:r2]) for x in range(l1,r1)) == bit.range_sum(l1,r1,l2,r2)

    MOD = 998244353
    mul = lambda x,y:x*y%MOD
    for m,n in product(range(1,10),range(1,10)):
        #for init in [None, [[i*j+1 for j in range(m)] for i in range(n)]]:
        for init in [None]:
            bit = FenwickTreeDual2d(n,m)
            if init == None: init = [[0]*m for _ in range(n)]
            # prefix_add query        
            for i,j in product(range(n+1),range(m+1)):
                bit.prefix_add(i,j,d:=i+j)
                for ii in range(i):
                    for jj in range(j):
                        init[ii][jj] += d
            
            # check get query
            for r1,r2 in product(range(n),range(m)):
                assert init[r1][r2] == bit.get(r1,r2)
            
        ################### check general    
        for init in [None]:
            bit = FenwickTreeDualGeneral2d(n,m,mul,1)
            if init == None: init = [[1]*m for _ in range(n)]
            
            # prefix_add query        
            for i,j in product(range(n+1),range(m+1)):
                bit.prefix_add(i,j,d:=i+j+1)
                for ii in range(i):
                    for jj in range(j):
                        init[ii][jj] *= d
                        init[ii][jj] %= MOD
            
            # check get query
            for r1,r2 in product(range(n),range(m)):
                assert init[r1][r2] == bit.get(r1,r2)
    






