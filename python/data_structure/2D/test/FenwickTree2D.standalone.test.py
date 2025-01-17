# competitive-verifier: STANDALONE

from python.data_structure.2D.FenwickTree2D import FenwickTree2D

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

