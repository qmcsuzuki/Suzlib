# competitive-verifier: STANDALONE

from itertools import product
from math import gcd

from python.math.number_theory.extgcd import extgcd
from python.math.number_theory.GridPointsOnLine import count_integer_points_of_queen_moves
from python.math.prime.Eratosthenes import Eratosthenes, Eratosthenes_is_prime_list
from python.math.prime.PrimeFactorize import prime_factorize
from python.math.prime.PrimitiveRoot import primitive_root, primitive_power_root
from python.math.prime.RangeSieve import RangeSieve
import python.math.number_theory.Garner as garner


if __name__ == "__main__":
    garner.MOD = 7
    assert garner.Garner([8],[11]) == 1
    for x in range(30):
        assert garner.Garner([x % 5, x % 6],[5,6]) == x % 7
    assert garner.Garner([0],[11],permit0=False) == 4
    for a,b in product(range(-10,11), repeat=2):
        g,x,y = extgcd(a,b)
        assert g == gcd(a,b) == a*x+b*y
    for n in range(101):
        expected = [k >= 2 and all(k % d for d in range(2,k)) for k in range(n+1)]
        assert Eratosthenes(n) == [k for k in range(n+1) if expected[k]]
        assert Eratosthenes_is_prime_list(n) == expected
        for l in range(n+1):
            assert RangeSieve(l,n)[1] == expected[l:]
    for n in range(1,101):
        value = 1
        for p,e in prime_factorize(n):
            value *= p**e
        assert value == n
    try:
        prime_factorize(0)
    except AssertionError:
        pass
    else:
        raise AssertionError("0 must be rejected")
    for a,b in product(range(-1,2), repeat=2):
        if a == b == 0:
            continue
        for c in range(-5,6):
            expected = sum(a*x+b*y == c for x in range(-2,4) for y in range(-3,2))
            assert count_integer_points_of_queen_moves(a,b,c,-2,4,-3,2) == expected
    for p in [3,5,7,11,13]:
        g = primitive_root(p)
        assert len({pow(g,k,p) for k in range(p-1)}) == p-1
        g = primitive_power_root(p,2)
        assert len({pow(g,k,p*p) for k in range(p*(p-1))}) == p*(p-1)
