# verification-helper: STANDALONE
import python.polynomial.LinearRecurrence as LinearRecurrence
import python.polynomial.simple_brute_polynomial as simple_brute_polynomial

MOD = 998244353
LinearRecurrence.MOD = MOD
simple_brute_polynomial.MOD = MOD


def build_sequence(initial, coeffs, n_max):
    k = len(coeffs)
    seq = initial[:]
    for i in range(k, n_max + 1):
        val = 0
        for j, coef in enumerate(coeffs):
            val += coef * seq[i - 1 - j]
        seq.append(val % MOD)
    return seq


def check_case(initial, coeffs):
    g = [1] + [(-coef) % MOD for coef in coeffs]
    seq = build_sequence(initial, coeffs, 100)
    for n in range(0, 101):
        got = LinearRecurrence.rec_nth_term(initial, g, n)
        expected = seq[n]
        assert got == expected, (n, got, expected)


def main():
    cases = [
        ([4, -5, 6, -7], [-1, 0, -2, 3]),
        ([1, 3], [0, 2]),
        ([2, 0, 5], [0, 0, 1]),
    ]
    for initial, coeffs in cases:
        check_case(initial, coeffs)

if __name__ == "__main__":
    main()
