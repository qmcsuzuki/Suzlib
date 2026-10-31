# competitive-verifier: STANDALONE
from collections import Counter
from itertools import combinations, combinations_with_replacement
from random import Random
from python.DP.subset_sum_fixed_k import (
    count_subset_sum, exists_subset_sum, find_subset_sum, _convolve_integer_binary, _convolve_frequency,
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
    if len(set(A)) == len(A):
        assert count_subset_sum(A, K, M, conv) == expected, (A, K, M)
    assert exists_subset_sum(A, K, M, conv) == (expected > 0), (A, K, M)
    ans = find_subset_sum(A, K, M, conv)
    assert (ans is not None) == (expected > 0), (A, K, M, ans)
    if ans is not None:
        assert len(ans) == K and sum(ans) == M
        assert not (Counter(ans) - Counter(A))
    assert A == original


def main():
    for mask in range(1 << 7):
        A = [i+1 for i in range(7) if mask >> i & 1]
        for K in (3, 4):
            for M in range(-1, 30):
                check(A, K, M, naive)
    for n in range(8):
        for A in combinations_with_replacement(range(1, 5), n):
            for K in (3, 4):
                for M in range(0, 18):
                    check(list(A), K, M, naive)
    for K in (3, 4):
        assert exists_subset_sum([2]*10000, K, 2*K, naive)
        assert find_subset_sum([2]*10000, K, 2*K, naive) == [2]*K
        assert not exists_subset_sum([2]*10000, K, 2*K+1, naive)
        assert find_subset_sum([2]*10000, K, 2*K+1, naive) is None
    rng = Random(0)
    for _ in range(100):
        A = rng.sample(range(1, 60), rng.randrange(15))
        for K in (3, 4):
            check(A, K, rng.randrange(241), convolution)
    for _ in range(100):
        A = [rng.randrange(1, 60) for _ in range(rng.randrange(20))]
        for K in (3, 4):
            check(A, K, rng.randrange(241), convolution)
    # 中間係数が法を超える場合も、桁分割で厳密に復元する。
    p, f = [MOD+5, 2*MOD+7, MOD*MOD+1], [1, 0, 1, 1]
    expected = [0]*(len(p)+len(f)-1)
    for i, x in enumerate(p):
        for j, y in enumerate(f):
            expected[i+j] += x*y
    assert _convolve_integer_binary(p, f, 3, convolution) == expected
    # 頻度列の係数が 1 を超え、畳み込み係数が法を超える場合。
    p, f = [MOD+5, 2*MOD+7], [3, 0, 4]
    expected = [3*p[0], 3*p[1], 4*p[0], 4*p[1]]
    assert _convolve_frequency(p, f, 7, convolution) == expected
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
    for A in ([0, 1, 2, 3], [-1, 2, 3, 4]):
        for func in (count_subset_sum, exists_subset_sum, find_subset_sum):
            try:
                func(A, 3, 6, naive)
            except AssertionError:
                pass
            else:
                raise AssertionError('invalid input accepted')
    try:
        count_subset_sum([1, 1, 2, 3], 3, 6, naive)
    except AssertionError:
        pass
    else:
        raise AssertionError('count accepted duplicate values')
    print('fixed-k subset sum: exhaustive, NTT, exact integer and recovery tests passed')


if __name__ == '__main__':
    main()

