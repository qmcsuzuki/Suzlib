# competitive-verifier: STANDALONE

from itertools import product
from random import Random

from python.data_structure.array1D.range_query.RangeAddRangeInnerproductMOD import RangeAddRangeInnerproductMOD


def check(seg,a,b,w):
    for l in range(len(a)+1):
        for r in range(l,len(a)+1):
            packed, sums = seg.prod(l,r)
            got_ab,got_w = divmod(packed,seg.M)
            got_a,got_b = divmod(sums,seg.M)
            assert got_ab == sum(w[i]*a[i]*b[i] for i in range(l,r)) % seg.MOD
            assert got_w == sum(w[l:r]) % seg.MOD
            assert got_a == sum(w[i]*a[i] for i in range(l,r)) % seg.MOD
            assert got_b == sum(w[i]*b[i] for i in range(l,r)) % seg.MOD


if __name__ == '__main__':
    rng = Random(20261002)
    # B 単独の初期値が無視されない。A 単独でも零列 B として構築できる。
    seg = RangeAddRangeInnerproductMOD(1,B=[3])
    seg.apply(0,1,seg.M)
    assert seg.prod(0,1)[0]//seg.M == 3
    for n in range(8):
        for use_a,use_b,use_w in product([False,True],repeat=3):
            a = [rng.randrange(-5,6) for _ in range(n)] if use_a else [0]*n
            b = [rng.randrange(-5,6) for _ in range(n)] if use_b else [0]*n
            w = [rng.randrange(-2,4) for _ in range(n)] if use_w else [1]*n
            seg = RangeAddRangeInnerproductMOD(n,a if use_a else None,b if use_b else None,w if use_w else None)
            check(seg,a,b,w)
            for _ in range(30):
                l,r = sorted([rng.randrange(n+1),rng.randrange(n+1)])
                p,q = rng.randrange(-5,6),rng.randrange(-5,6)
                seg.apply(l,r,(p % seg.MOD)*seg.M + q % seg.MOD)
                for i in range(l,r):
                    a[i] += p
                    b[i] += q
                check(seg,a,b,w)
