# competitive-verifier: PROBLEM https://onlinejudge.u-aizu.ac.jp/problems/DSL_3_D
# http://judge.u-aizu.ac.jp/onlinejudge/review.jsp?rid=4953425#1

from python.data_structure.array1D.SlidingWindowMinMax import SlidingWindowMaximum
from python.data_structure.array1D.SlidingWindowMinMax import SlidingWindowMinimum
import sys
readline = sys.stdin.readline

n,l = map(int,readline().split())
*a, = map(int,readline().split())

datmin = SlidingWindowMinimum(a)
datmin_by_max = SlidingWindowMaximum([-i for i in a])

ans = [0]*(n-l+1)
for i in range(n-l+1):
    ans[i] = datmin.query(i,i+l)
    assert ans[i] == -datmin_by_max.query(i,i+l)
print(*ans)
