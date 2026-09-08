# competitive-verifier: TITLE 約数包除（large N）


from python.math.prime.divisors_and_prime_divisors import divisors_and_prime_divisors

class DivisorTransform:
    """
    n の約数束上の zeta / mobius 変換。
    lower: F(d) = sum_{c|d} f(c)
    upper: F(d) = sum_{d|c|n} f(c)
    """
    def __init__(self, n: int, divs=None, primes=None):
        """変換対象 n の整列済み約数列と素因数列を用意する。"""
        self.n = n
        if divs is None and primes is None:
            self.divs, self.primes = divisors_and_prime_divisors(n)
        else:
            assert divs is not None and primes is not None
            self.divs = sorted(divs)
            self.primes = list(primes)

    def zeta_lower(self, a: dict[int, int]) -> dict[int, int]:
        """F(d) = sum_{c | d} f(c)."""
        a = a.copy()
        self.zeta_lower_inplace(a)
        return a

    def mobius_lower(self, a: dict[int, int]) -> dict[int, int]:
        """zeta_lower の逆変換。"""
        a = a.copy()
        self.mobius_lower_inplace(a)
        return a

    def zeta_upper(self, a: dict[int, int]) -> dict[int, int]:
        """F(d) = sum_{d | c | n} f(c)."""
        a = a.copy()
        self.zeta_upper_inplace(a)
        return a

    def mobius_upper(self, a: dict[int, int]) -> dict[int, int]:
        """zeta_upper の逆変換。"""
        a = a.copy()
        self.mobius_upper_inplace(a)
        return a

    def zeta_lower_inplace(self, a: dict[int, int]) -> None:
        """約数側からの和を取るゼータ変換で入力辞書を上書きする。"""
        for p in self.primes:
            for d in self.divs:
                if d % p == 0:
                    a[d] += a[d // p]

    def mobius_lower_inplace(self, a: dict[int, int]) -> None:
        """約数側のゼータ変換を反転して入力辞書を上書きする。"""
        for p in self.primes:
            for d in reversed(self.divs):
                if d % p == 0:
                    a[d] -= a[d // p]

    def zeta_upper_inplace(self, a: dict[int, int]) -> None:
        """倍数側からの和を取るゼータ変換で入力辞書を上書きする。"""
        for p in self.primes:
            for d in reversed(self.divs):
                dp = d * p
                if self.n % dp == 0:
                    a[d] += a[dp]

    def mobius_upper_inplace(self, a: dict[int, int]) -> None:
        """倍数側のゼータ変換を反転して入力辞書を上書きする。"""
        for p in self.primes:
            for d in self.divs:
                dp = d * p
                if self.n % dp == 0:
                    a[d] -= a[dp]
