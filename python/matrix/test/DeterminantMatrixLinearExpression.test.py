# competitive-verifier: PROBLEM https://yukicoder.me/problems/no/1907

import sys

import python.matrix.DeterminantMatrixLinearExpression as dmle

MOD = 998244353
dmle.MOD = MOD
readline = sys.stdin.readline


def main():
    n = int(readline())
    M0 = [list(map(int, readline().split())) for _ in range(n)]
    M1 = [list(map(int, readline().split())) for _ in range(n)]
    print(*dmle.determinant_matrix_linear_expression(M0, M1), sep="\n")


if __name__ == "__main__":
    main()
