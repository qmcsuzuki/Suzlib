# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/point_add_range_sum

from python.data_structure.FenwickTree.FenwickTree import FenwicTree
import sys
readline = sys.stdin.readline

def main():
    n,Q = map(int,readline().split())
    *a, = map(int,readline().split())
    bit = FenwickTree(n,a)
    for _ in range(Q):
        t,i,x = map(int,readline().split())
        if t==0:
            bit.add(i,x)
        else:
            print(bit.range_sum(i,x))

if __name__ == '__main__':
    main()
