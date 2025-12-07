# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/predecessor_problem

from python.data_structure.array1D.FenwickTree import FenwickTree
from python.data_structure.array1D.OrderedMultisetWithZaat import OrderedMultisetWithZaat
import sys
readline = sys.stdin.readline

def main():
n,Q = map(int,readline().split())
T = readline().strip()

m,M = -1,n #番兵
S = OrderedMultisetWithZaatu(range(n), m, M)
for i in range(n):
    if T[i] == "1":
        S.add(i)

for _ in range(Q):
    c,k = map(int,readline().split())
    if c == 0:
        if k not in S:
            S.add(k)
    elif c == 1:
        if k in S:
            S.delete(k)
    elif c == 2:
        print(int(k in S))
    elif c == 3:
        r = S.next_value(k-1)
        print(r if r != M else -1)
    elif c == 4:
        r = S.prev_value(k+1)
        print(r if r != m else -1)

if __name__ == '__main__':
    main()
