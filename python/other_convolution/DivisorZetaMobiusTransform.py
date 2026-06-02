# competitive-verifier: TITLE 約数包除（large N）


from python.math.prime.divisors_and_prime_divisors import divisors_and_prime_divisors

class DivisorTransform:
    """
    n の約数束上の zeta / mobius 変換。
    lower: F(d) = sum_{c|d} f(c)
    upper: F(d) = sum_{d|c|n} f(c)
    """
    def __init__(self, n, divs=None, primes=None):
        self.n = n
        if divs is None and primes is None:
            self.divs, self.primes = divisors_and_prime_divisors(n)
        else:
            self.divs = sorted(divs)
            self.primes = list(primes)
        self.pos = {d: i for i, d in enumerate(self.divs)}

        self.lower_edges = []
        self.upper_edges = []

        for p in self.primes:
            lower = []
            upper = []
            for d in self.divs:
                if d % p == 0:
                    lower.append((self.pos[d], self.pos[d // p]))

                dp = d * p
                if self.n % dp == 0:
                    upper.append((self.pos[d], self.pos[dp]))

            self.lower_edges.append(lower)
            self.upper_edges.append(upper)

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
        for p in self.primes:
            for d in self.divs:
                if d % p == 0:
                    a[d] += a[d // p]

    def mobius_lower_inplace(self, a: dict[int, int]) -> None:
        for p in self.primes:
            for d in reversed(self.divs):
                if d % p == 0:
                    a[d] -= a[d // p]

    def zeta_upper_inplace(self, a: dict[int, int]) -> None:
        for p in self.primes:
            for d in reversed(self.divs):
                dp = d * p
                if self.n % dp == 0:
                    a[d] += a[dp]

    def mobius_upper_inplace(self, a: dict[int, int]) -> None:
        for p in self.primes:
            for d in self.divs:
                dp = d * p
                if self.n % dp == 0:
                    a[d] -= a[dp]
