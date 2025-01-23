# verification-helper: PROBLEM https://judge.yosupo.jp/problem/matrix_product

from python.matrix.ModMatrix import ModMatrixBase
import sys
readline = sys.stdin.readline

class ModMatrix998(ModMatrixBase):
    MOD = 998244353
Mat = ModMatrix998

n,m,k = map(int,readline().split())
A = Mat(n,m,[list(map(int,readline().split())) for _ in range(n)])
B = Mat(m,k,[list(map(int,readline().split())) for _ in range(m)])
C = A*B

print(C)
