# competitive-verifier: STANDALONE
from itertools import combinations
from random import Random
from python.DP.subset_sum_fixed_k import (
    count_subset_sum, find_subset_sum, _convolve_integer_binary,
)

MOD = 998244353


def convolution(a, b):
    # 外部依存なしの検証用 NTT（本体は呼び出し側から渡す設計）。
    def ntt(a, inverse):
        n = len(a)
        j = 0
        for i in range(1, n):
            bit = n >> 1
            while j & bit:
                j ^= bit
                bit >>= 1
            j ^= bit
            if i < j:
                a[i], a[j] = a[j], a[i]
        length = 2
        while length <= n:
            root = pow(3, (MOD-1)//length, MOD)
            if inverse:
                root = pow(root, MOD-2, MOD)
            for i in range(0, n, length):
                w = 1
                for j in range(i, i+length//2):
                    u, v = a[j], a[j+length//2]*w % MOD
                    a[j] = (u+v) % MOD
                    a[j+length//2] = (u-v) % MOD
                    w = w*root % MOD
            length *= 2
        if inverse:
            inv = pow(n, MOD-2, MOD)
            for i in range(n):
                a[i] = a[i]*inv % MOD
    size = len(a)+len(b)-1
    length = 1 << (size-1).bit_length()
    a, b = a[:] + [0]*(length-len(a)), b[:] + [0]*(length-len(b))
    ntt(a, False)
    ntt(b, False)
    a = [x*y % MOD for x, y in zip(a, b)]
    ntt(a, True)
    return a[:size]


def naive(a, b):
    c = [0]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i+j] += x*y
    return [v % MOD for v in c]


def check(A, K, M, conv):
    expected = sum(sum(c) == M for c in combinations(A, K))
    original = A[:]
    assert count_subset_sum(A, K, M, conv) == expected, (A, K, M)
    ans = find_subset_sum(A, K, M, conv)
    assert (ans is not None) == (expected > 0), (A, K, M, ans)
    if ans is not None:
        assert len(ans) == len(set(ans)) == K and sum(ans) == M
        assert set(ans) <= set(A)
    assert A == original


def main():
    for mask in range(1 << 7):
        A = [i+1 for i in range(7) if mask >> i & 1]
        for K in (3, 4):
            for M in range(-1, 30):
                check(A, K, M, naive)
    rng = Random(0)
    for _ in range(100):
        A = rng.sample(range(1, 60), rng.randrange(15))
        for K in (3, 4):
            check(A, K, rng.randrange(241), convolution)
    # 中間係数が法を超える場合も、桁分割で厳密に復元する。
    p, f = [MOD+5, 2*MOD+7, MOD*MOD+1], [1, 0, 1, 1]
    expected = [0]*(len(p)+len(f)-1)
    for i, x in enumerate(p):
        for j, y in enumerate(f):
            expected[i+j] += x*y
    assert _convolve_integer_binary(p, f, 3, convolution) == expected
    # 真の答え > mod。独立な Gaussian binomial の係数計算と照合。
    n, K, M = 4000, 4, 8002
    degree = M-K*(K+1)//2
    dp = [1] + [0]*degree
    for i in range(1, K+1):
        for s in range(i, degree+1):
            dp[s] += dp[s-i]
        shift = n-K+i
        for s in range(degree, shift-1, -1):
            dp[s] -= dp[s-shift]
    assert dp[-1] > MOD
    A = list(range(1, n+1))
    assert count_subset_sum(A, K, M, convolution) == dp[-1]
    ans = find_subset_sum(A, K, M, convolution)
    assert len(set(ans)) == K and sum(ans) == M and set(ans) <= set(A)
    for A in ([1, 1, 2, 3], [0, 1, 2, 3], [-1, 2, 3, 4]):
        for func in (count_subset_sum, find_subset_sum):
            try:
                func(A, 3, 6, naive)
            except AssertionError:
                pass
            else:
                raise AssertionError('invalid input accepted')
    print('fixed-k subset sum: exhaustive, NTT, exact integer and recovery tests passed')


if __name__ == '__main__':
    main()
