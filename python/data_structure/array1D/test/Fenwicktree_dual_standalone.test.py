# competitive-verifier: STANDALONE

from python.data_structure.array1D.FenwickTreeDual import FenwickTreeDual
from python.data_structure.array1D.SegmentTreeDual import SegmentTreeDual


if __name__ == "__main__":
    add = lambda x,y:x+y
    for n in range(1,10):
        for init in [None,range(n)]:
            seg1 = SegmentTreeDual(n, add, 0, False, init, add)
            seg2 = SegmentTreeDual(n, add, 0, True , init, add)
            bit1 = FenwickTreeDual(n, init)
            bit2 = FenwickTreeDual(n, init)
            
            if init == None: brute = [0]*n
            else: brute = list(init)
            
            for i in range(n):
                # check point_set
                seg1.point_set(i,i)
                seg2.point_set(i,i)
                bit1.range_add(i,i+1, i - bit1.point_get(i))
                bit2.range_add(i,i+1, i - bit2.point_get(i))
                brute[i] = i
                
                for j in range(i,n):
                    for k in range(i,j):
                        brute[k] += i*j
                    
                    seg1.apply(i,j,i*j)
                    seg2.apply(i,j,i*j)
                    bit1.range_add(i,j,i*j)
                    bit2.range_add(i,j,i*j)
                
                for k in range(n):
                    v1 = seg1.point_get(k)
                    v2 = seg2.point_get(k)
                    w1 = seg1.apply_to_point(k,0)
                    w2 = seg2.apply_to_point(k,0)
                    x1 = bit1.point_get(k)
                    x2 = bit2.point_get(k)
                    assert brute[k]==v1==v2==w1==w2==x1==x2
            
            assert brute == seg1.all_get() == seg2.all_get() == bit1.all_get() == bit2.all_get()
