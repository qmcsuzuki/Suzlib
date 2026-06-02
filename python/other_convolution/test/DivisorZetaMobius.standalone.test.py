# competitive-verifier: STANDALONE

from random import Random

from python.math.prime.Eratosthenes import Eratosthenes
from python.math.prime.divisors_and_prime_divisors import divisors_and_prime_divisors
from python.other_convolution.DivisorZetaMobiusTransform import DivisorTransform
import python.other_convolution.DivisorZetaMobius_allN as allN

MOD = 998244353
allN.MOD = MOD


def brute_lower(a):
    n = len(a) - 1
    res = [0] * (n + 1)
    for d in range(1, n + 1):
        s = 0
        for c in range(1, d + 1):
            if d % c == 0:
                s += a[c]
        res[d] = s % MOD
    return res


def brute_upper(a):
    n = len(a) - 1
    res = [0] * (n + 1)
    for d in range(1, n + 1):
        s = 0
        for c in range(d, n + 1, d):
            s += a[c]
        res[d] = s % MOD
    return res


def check_allN(a, primes):
    lower = brute_lower(a)
    upper = brute_upper(a)

    b = a[:]
    allN.zeta_gcd_to_n(b, primes)
    assert b == lower
    allN.zeta_mobius_to_n(b, primes)
    assert b == a

    b = a[:]
    allN.zeta_gcd(b, primes)
    assert b == upper
    allN.mobius_gcd(b, primes)
    assert b == a


def check_divisor_transform(n, a, primes):
    divs, prime_divs = divisors_and_prime_divisors(n)
    sparse = [0] * (n + 1)
    for d in divs:
        sparse[d] = a[d]

    lower = brute_lower(sparse)
    upper = brute_upper(sparse)
    dt = DivisorTransform(n, divs, prime_divs)
    dt2 = DivisorTransform(n)
    f = {d: sparse[d] for d in divs}
    lower_dict = {d: lower[d] for d in divs}
    upper_dict = {d: upper[d] for d in divs}

    assert dt.divs == dt2.divs == divs
    assert dt.primes == dt2.primes == prime_divs
    assert dt.zeta_lower(f) == dt2.zeta_lower(f) == lower_dict
    assert dt.mobius_lower(lower_dict) == dt2.mobius_lower(lower_dict) == f
    assert dt.zeta_upper(f) == dt2.zeta_upper(f) == upper_dict
    assert dt.mobius_upper(upper_dict) == dt2.mobius_upper(upper_dict) == f

    b = sparse[:]
    allN.zeta_gcd_to_n(b, primes)
    assert {d: b[d] for d in divs} == dt.zeta_lower(f)
    allN.zeta_mobius_to_n(b, primes)
    assert {d: b[d] for d in divs} == f

    b = sparse[:]
    allN.zeta_gcd(b, primes)
    assert {d: b[d] for d in divs} == dt.zeta_upper(f)
    allN.mobius_gcd(b, primes)
    assert {d: b[d] for d in divs} == f


if __name__ == "__main__":
    N = 100
    primes = Eratosthenes(N)
    rng = Random(0)

    # N 程度の長さの配列で、N 以下全体の 4 種類の変換を愚直と比較する。
    for _ in range(100):
        a = [0] + [rng.randrange(1000) for _ in range(N)]
        check_allN(a, primes)

    # 各 n の約数束でも、愚直・large N 版・allN 版が一致することを確認する。
    for n in range(1, N + 1):
        for _ in range(10):
            a = [0] + [rng.randrange(1000) for _ in range(n)]
            check_divisor_transform(n, a, primes)
