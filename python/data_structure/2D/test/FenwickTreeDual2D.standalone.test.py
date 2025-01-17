from python.data_structure.2D.FenwickTreeDual2D import FenwickTreeDual2D
from python.data_structure.2D.FenwickTreeDualGeneral2D import FenwickTreeDualGeneral2D


if __name__ == "__main__":
    from itertools import product
    # test Gemera;FenwickTree2d
    MOD = 998244353
    mul = lambda x,y:x*y%MOD
    for m,n in product(range(1,10),range(1,10)):
        ################### check general    
        for init in [None]:
            bit = FenwickTreeDualGeneral2D(n,m,mul,1)
            bitS = FenwickTreeDualGeneral2DSuffix(n,m,mul,1)
            if init == None:
                init = [[1]*m for _ in range(n)]
                initS = [[1]*m for _ in range(n)]
            else:
                initS = [list(row) for row in init]
            
            # prefix_add query        
            for i,j in product(range(n+1),range(m+1)):
                bit.prefix_add(i,j,d:=i+j+1)
                bitS.suffix_add(i,j,d:=i+j+1)
                for ii in range(i):
                    for jj in range(j):
                        init[ii][jj] *= d
                        init[ii][jj] %= MOD
                for ii in range(i,n):
                    for jj in range(j,m):
                        initS[ii][jj] *= d
                        initS[ii][jj] %= MOD
    
            # check get query
            for r1,r2 in product(range(n),range(m)):
                assert init[r1][r2] == bit.get(r1,r2)
                assert initS[r1][r2] == bitS.get(r1,r2)
    
    
    
    
