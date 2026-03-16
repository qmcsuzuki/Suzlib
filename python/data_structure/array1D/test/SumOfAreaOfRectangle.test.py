# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/area_of_union_of_rectangles

import sys
from python.data_structure.array1D.SumOfAreaOfRectangle import AreaOfUnionOfRectangles

readline = sys.stdin.readline

N = int(readline())
solver = AreaOfUnionOfRectangles()
for _ in range(N):
    l, d, r, u = map(int, readline().split())
    solver.add_query(l, d, r, u)

print(solver.solve_with_zaatu())
