# competitive-verifier: STANDALONE

from python.data_structure_2D.FenwickTree2D import FenwickTree2D

if __name__ == "__main__":
    from itertools import product
    # test FenwickTree2d
    for m,n in product(range(1,10),range(1,10)):
        init = [[i*j+1 for j in range(m)] for i in range(n)]]
        bit0 = FenwickTree2D(n,m,init)
        bit1 = FenwickTree2D(n,m)
        for i,j in product(range(n),range(m)):
            bit0.add(i,j,d:=i-j)
            bit1.add(i,j,d+i*j+1)
            init[i][j] += d
        
        # check range query
        for r1,r2 in product(range(n+1),range(m+1)):
            Lsum,Rsum = sum(sum(init[x][:r2]) for x in range(r1)), sum(sum(init[x][r2:]) for x in range(r1,n))
            assert Lsum == bit0.prefix_sum(r1,r2) == bit1.prefix_sum(r1,r2)
            assert Rsum == bit0.suffix_sum(r1,r2) == bit1.prefix_sum(r1,r2)
            
            for l1,l2 in product(range(r1+1),range(r2+1)):
                rangesum = sum(sum(init[x][l2:r2]) for x in range(l1,r1))
                assert rangesum == bit0.range_sum(l1,r1,l2,r2) == bit1.range_sum(l1,r1,l2,r2)

