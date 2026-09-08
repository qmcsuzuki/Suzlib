# competitive-verifier: STANDALONE

from random import Random

from python.data_structure.array1D.AddAbsGetValOffline import AddAbsGetValOffline
from python.data_structure.array1D.Inversion import inversion_distance
from python.data_structure.array1D.SlidingWindowAggregation import SWAG
from python.data_structure.array1D.SortedArrayInnerProduct import SortedArrayInnerProduct
from python.data_structure.array1D.LazySegmentTree import LazySegmentTree
from python.data_structure.array1D.SegmentTreeDual import SegmentTreeDual
from python.data_structure.array1D.range_query.RangeAddPointGet import RangeAddPointGet
from python.data_structure.array1D.range_query.RangeAddRangeSum import RangeAddRangeSum
from python.data_structure.array1D.range_query.RangeAddRangeInnerproductMOD import RangeAddRangeInnerproductMOD
from python.data_structure.array1D.range_query.RangeAffineRangeSum import RangeAffineRangeSumMOD998244353
from python.data_structure.array1D.range_query.RangeUpdateFlipRangeSum01 import RangeUpdateFlipRangeSum01
import python.data_structure.array1D.range_query.RangeAddRangeSquareMOD as square
from python.data_structure.heap.DeletableHeapq import DeletableHeapqInt


if __name__ == "__main__":
    rng = Random(82)
    for init in [[], ['a'], ['a','b','c']]:
        q = SWAG(str.__add__, '', init)
        expected = init[:]
        for _ in range(100):
            if expected and rng.randrange(2):
                assert q.popleft() == expected.pop(0)
            else:
                x = str(rng.randrange(10))
                q.append(x)
                expected.append(x)
            assert len(q) == len(expected)
            assert q.fold_all() == ''.join(expected)
    assert inversion_distance([0],[0,0]) == -1
    assert inversion_distance([0,0],[0]) == -1
    assert DeletableHeapqInt(iter([2,3])).sum == 5

    coords = [-5,0,3,10]
    za = {v:i for i,v in enumerate(coords)}
    f = AddAbsGetValOffline(coords,za)
    for x in coords:
        f.add_abs(x,1,1)
    for x in range(-10,16):
        assert f.getval(x,False) == sum(abs(x-p) for p in coords)
    assert f.getmin() == min(sum(abs(x-p) for p in coords) for x in coords)
    for reverse in [False,True]:
        f = SortedArrayInnerProduct(2,3,len(coords)-1,reverse,za,coords)
        a = coords[:]
        for _ in range(100):
            if a and rng.randrange(2):
                x = rng.choice(a)
                a.remove(x)
                f.remove_before_zaatu(x)
            else:
                x = rng.choice(coords)
                a.append(x)
                f.insert_before_zaatu(x)
            assert f.getvalue() == sum((2*i+3)*x for i,x in enumerate(sorted(a,reverse=reverse)))

    square.MOD = mod = 998244353
    for n in range(1,8):
        a = [rng.randrange(5) for _ in range(n)]
        point = RangeAddPointGet(n,a)
        total = RangeAddRangeSum(n,a)
        sq = square.RangeAddRangeSquareMOD(n,a)
        affine = RangeAffineRangeSumMOD998244353(n,a)
        ab = RangeAddRangeInnerproductMOD(n)
        aa,bb = [0]*n,[0]*n
        binary = RangeUpdateFlipRangeSum01([x % 2 for x in a])
        bits = [x % 2 for x in a]
        for _ in range(40):
            l,r = sorted([rng.randrange(n+1),rng.randrange(n+1)])
            x = rng.randrange(5)
            point.range_add(l,r,x)
            total.range_add(l,r,x)
            sq.apply(l,r,x)
            affine.range_add(l,r,x)
            ab.apply(l,r,x*ab.M+2)
            binary.range_flip(l,r)
            for i in range(l,r):
                a[i] += x
                aa[i] += x
                bb[i] += 2
                bits[i] ^= 1
            assert point.all_get() == a
            assert [point.point_get(i) for i in range(n)] == a
            assert total.range_sum(l,r) == sum(a[l:r])
            assert sq.prod(l,r)[2] == sum(x*x for x in a[l:r]) % mod
            assert affine.range_sum(l,r) == sum(a[l:r]) % mod
            assert ab.prod(l,r)[0] // ab.M == sum(x*y for x,y in zip(aa[l:r],bb[l:r])) % mod
            assert binary.range_sum(l,r) == sum(bits[l:r])
        str(SegmentTreeDual(n,min,10**9))
    str(LazySegmentTree(min,10**9,lambda f,x:f+x,int.__add__,0,1,[0]))
