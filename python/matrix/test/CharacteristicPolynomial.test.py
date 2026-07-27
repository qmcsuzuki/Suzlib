# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/characteristic_polynomial

import sys

import python.matrix.DeterminantMatrixLinearExpression as dmle

MOD = 998244353
dmle.MOD = MOD
readline = sys.stdin.readline


def main():
    n = int(readline())
    A = [list(map(int, readline().split())) for _ in range(n)]
    print(*dmle.characteristic_polynomial(A))


if __name__ == "__main__":
    main()
