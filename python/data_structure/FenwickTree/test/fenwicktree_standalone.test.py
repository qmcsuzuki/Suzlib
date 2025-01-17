# competitive-verifier: STANDALONE

#from python.data_structure.FenwickTree.FenwickTree import FenwickTree
from ..FenwickTree import FenwickTree
import sys
readline = sys.stdin.readline

if __name__ == "__main__":
    for n in range(1,10):
        for init in [None,range(n)]:
            bit = FenwickTree(n,init)
            if init == None: init = [0]*n
            else: init = list(init)
            
            for i in range(n):
                bit.add(i,i)
                init[i] += i
            
            # check range query
            for i in range(n+1):
                assert sum(init[:i]) == bit.prefix_sum(i)
                assert sum(init[i:]) == bit.suffix_sum(i)
                for j in range(i,n+1):
                    assert sum(init[i:j]) == bit.range_sum(i,j)
             
            # check bisect
            for x in range(-10,80):
                idx = bit.bisect_left(x)
                assert idx==n or bit.prefix_sum(idx+1) >= x
                assert x <= 0 or bit.prefix_sum(idx) < x

