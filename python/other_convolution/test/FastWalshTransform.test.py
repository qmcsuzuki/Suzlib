# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/bitwise_xor_convolution

import sys

import python.other_convolution.FastWalshTransform as fwt

MOD = 998244353
fwt.MOD = MOD
readline = sys.stdin.readline


def main():
    n = int(readline())
    a = list(map(int, readline().split()))
    b = list(map(int, readline().split()))
    fwt.fwt_inplace(a)
    fwt.fwt_inplace(b)
    for i in range(1 << n):
        a[i] = a[i] * b[i] % MOD
    fwt.ifwt_inplace(a)
    print(*a)


if __name__ == "__main__":
    main()
