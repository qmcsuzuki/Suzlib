# verification-helper: PROBLEM https://judge.yosupo.jp/problem/find_linear_recurrence
from python.polynomial.simple_brute_polynomial import polymul
import python.polynomial.LinearRecurrence as LinearRecurrence


def main():
    n = int(input())
    a = list(map(int, input().split()))
    LinearRecurrence.MOD = 998244353
    LinearRecurrence.polymul = polymul
    _, q = LinearRecurrence.Berlecamp_Massay(a)
    k = len(q) - 1
    coeffs = [(-q[i]) % LinearRecurrence.MOD for i in range(1, k + 1)]
    coeffs.reverse()
    print(k)
    if k > 0:
        print(" ".join(map(str, coeffs)))


if __name__ == "__main__":
    main()
