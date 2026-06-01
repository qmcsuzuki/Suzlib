# competitive-verifier: TITLE 約数包除（large N）


class DivisorTransform:
    """
    n の約数束上の zeta / mobius 変換。
    lower: F(d) = sum_{c|d} f(c)
    upper: F(d) = sum_{d|c|n} f(c)
    """

    def __init__(self, n, divs, primes):
        self.n = n
        self.divs = sorted(divs)
        self.pos = {d: i for i, d in enumerate(self.divs)}
        self.primes = list(primes)

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

    def zeta_lower(self, a):
        """F(d) = sum_{c | d} f(c)."""
        a = a[:]
        self.zeta_lower_inplace(a)
        return a

    def mobius_lower(self, a):
        """zeta_lower の逆変換。"""
        a = a[:]
        self.mobius_lower_inplace(a)
        return a

    def zeta_upper(self, a):
        """F(d) = sum_{d | c | n} f(c)."""
        a = a[:]
        self.zeta_upper_inplace(a)
        return a

    def mobius_upper(self, a):
        """zeta_upper の逆変換。"""
        a = a[:]
        self.mobius_upper_inplace(a)
        return a

    def zeta_lower_inplace(self, a):
        for edges in self.lower_edges:
            for i, j in edges:
                a[i] += a[j]

    def mobius_lower_inplace(self, a):
        for edges in self.lower_edges:
            for i, j in reversed(edges):
                a[i] -= a[j]

    def zeta_upper_inplace(self, a):
        for edges in self.upper_edges:
            for i, j in reversed(edges):
                a[i] += a[j]

    def mobius_upper_inplace(self, a):
        for edges in self.upper_edges:
            for i, j in edges:
                a[i] -= a[j]
