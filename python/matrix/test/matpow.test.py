# verification-helper: PROBLEM https://judge.yosupo.jp/problem/pow_of_matrix

from python.matrix.ModMatrix import ModMatrixBase
import sys
readline = sys.stdin.readline

class ModMatrix998(ModMatrixBase):
    MOD = 998244353
Mat = ModMatrix998

n,k = map(int,readline().split())
A = Mat(n,n,[list(map(int,readline().split())) for _ in range(n)])
C = A**k

print(C)
