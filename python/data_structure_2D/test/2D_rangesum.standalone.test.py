# competitive-verifier: STANDALONE

from python.data_structure_2D.FenwickTree2D import FenwickTree2D
from python.data_structure_2D.Accumulate2dim import Accumulate2dim
from python.data_structure_2D.SegmentTree2D import SegmentTree2D

if __name__ == "__main__":
    from itertools import product
    from operator import add
    # test FenwickTree2d
    for n,m in product(range(1,10),range(1,10)):
        init = [[i*j+1 for j in range(m)] for i in range(n)]
        bit0 = FenwickTree2D(n,m,init)
        bit1 = FenwickTree2D(n,m)
        seg0 = SegmentTree2D(n,m,add,0,init)
        seg1 = SegmentTree2D(n,m,add,0)
        for i,j in product(range(n),range(m)):
            bit0.add(i,j,d:=i-j)
            bit1.add(i,j,d+i*j+1)
            seg0.update(i,j,seg0.get(i,j)+d)
            seg1.update(i,j,d)            
            init[i][j] += d
        acc = Accumulate2dim(init)
        
        # check range query
        assert seg0.all_prod() == seg1.all_prod() == acc.prefix_sum(n,m)
        for r1,r2 in product(range(n+1),range(m+1)):
            Lsum,Rsum = sum(sum(init[x][:r2]) for x in range(r1)), sum(sum(init[x][r2:]) for x in range(r1,n))
            assert Lsum == bit0.prefix_sum(r1,r2) == bit1.prefix_sum(r1,r2) == acc.prefix_sum(r1,r2)
            assert Rsum == bit0.suffix_sum(r1,r2) == bit1.suffix_sum(r1,r2)
            
            for l1,l2 in product(range(r1+1),range(r2+1)):
                rangesum = sum(sum(init[x][l2:r2]) for x in range(l1,r1))
                assert (rangesum == bit0.range_sum(l1,r1,l2,r2) == bit1.range_sum(l1,r1,l2,r2)
                        == acc.range_sum(l1,r1,l2,r2)
                        == seg0.prod(l1,r1,l2,r2) == seg1.prod(l1,r1,l2,r2))



