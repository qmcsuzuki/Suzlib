# competitive-verifier: STANDALONE

from heapq import heappop, heappush
from itertools import product
from operator import add, xor
from random import Random

from python.graph.grid.BFS01 import BFS01
from python.misc.DAGof2dPoints import DAGof2dPoints
from python.data_structure.array1D.FenwickTree import FenwickTree
from python.data_structure.array1D.FenwickTreeGeneral import FenwickTreeGeneral
from python.data_structure.array1D.OrderedMultisetZaatu import OrderedMultisetWithZaatu, OrderedMultisetWithSumWithZaatu
from python.math.prime.MultiplePrimeFactorize import Eratosthenes_spf_list, factorize
from python.string.KMP import KMP, prefix_function


def check_bfs(board, starts, cost_one):
    h, w = len(board), len(board[0])
    expected = [[1 << 60] * w for _ in range(h)]
    heap = []
    for x,y in starts:
        expected[x][y] = 0
        heappush(heap, (0,x,y))
    while heap:
        d,x,y = heappop(heap)
        if d != expected[x][y]: continue
        for nx,ny in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
            if not (0 <= nx < h and 0 <= ny < w) or board[nx][ny] == 'X': continue
            nd = d + (board[nx][ny] == cost_one)
            if nd < expected[nx][ny]:
                expected[nx][ny] = nd
                heappush(heap, (nd,nx,ny))
    assert BFS01(board, starts, cost_one) == expected


if __name__ == '__main__':
    rng = Random(123)
    assert BFS01([], []) == []
    assert BFS01([[]], []) == [[]]
    assert BFS01([[1,0,1]], [(0,0)]) == [[0,1,1]]
    for marker in [0, '#']:
        for _ in range(100):
            board = [[rng.choice([marker, '.', 'X']) for _ in range(5)] for _ in range(4)]
            starts = [(x,y) for x in range(4) for y in range(5) if board[x][y] != 'X' and rng.randrange(4) == 0]
            check_bfs(board, starts, marker)

    for xr,yr in product([False,True], repeat=2):
        assert DAGof2dPoints([], xr,yr) == []
        assert DAGof2dPoints([(2,3)], xr,yr) == [[]]
        try:
            DAGof2dPoints([(1,2),(3,4),(1,2)], xr,yr)
        except AssertionError:
            pass
        else:
            raise AssertionError('duplicate points must be rejected')

    bit = FenwickTree(0, init=[])
    assert bit.prefix_sum(0) == bit.range_sum(0,0) == bit.suffix_sum(0) == 0
    for w in [-1,0,1]:
        assert bit.bisect_left(w) == bit.bisect_left_key(w, lambda x:x) == 0
    for op,inv in [(add,lambda x:-x),(xor,lambda x:x)]:
        for n in range(20):
            values = [rng.randrange(16) for _ in range(n)]
            bit = FenwickTreeGeneral(n,op,0,inv,init=iter(values))
            for _ in range(10):
                if n:
                    i,x = rng.randrange(n), rng.randrange(16)
                    values[i] = op(values[i],x)
                    bit.add(i,x)
                for l in range(n+1):
                    acc = 0
                    for r in range(l,n+1):
                        assert bit.range_sum(l,r) == acc
                        if r == n: assert bit.suffix_sum(l) == acc
                        if l == 0: assert bit.prefix_sum(r) == acc
                        if r < n: acc = op(acc,values[r])

    for cls in [OrderedMultisetWithZaatu, OrderedMultisetWithSumWithZaatu]:
        for candidates in [[],[0,1,2]]:
            s = cls(iter(candidates), -10,10)
            values = candidates + candidates
            for v in values: s.add(v)
            for v in range(-11,12):
                assert s.count_eq(v) == values.count(v)
                assert s.count_less(v) == sum(x < v for x in values)
                assert s.count_ge(v) == sum(x >= v for x in values)
            if hasattr(s, 'sum_eq'):
                assert s.sum_eq(-10) == s.sum_eq(10) == 0

    spf = Eratosthenes_spf_list(1000)
    for n in range(1,1001):
        got = factorize(n,spf)
        assert got == factorize(n)
        acc = 1
        for p in got:
            assert p >= 2 and all(p % d for d in range(2, int(p**0.5)+1))
            acc *= p
        assert acc == n
    assert factorize(0,spf) == []
    assert factorize(1,Eratosthenes_spf_list(1)) == []

    for n in range(6):
        for chars in product('ab', repeat=n):
            text = ''.join(chars)
            for m in range(4):
                for pc in product('ab', repeat=m):
                    pattern = ''.join(pc)
                    expected = sum(text[i:i+m] == pattern for i in range(n-m+1))
                    assert KMP(text,pattern,prefix_function(pattern)) == expected
