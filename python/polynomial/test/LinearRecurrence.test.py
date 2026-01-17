# verification-helper: PROBLEM https://judge.yosupo.jp/problem/find_linear_recurrence
import python.polynomial.LinearRecurrence as LinearRecurrence
import python.polynomial.simple_brute_polynomial as simple_brute_polynomial

MOD = 998244353
LinearRecurrence.MOD = MOD
simple_brute_polynomial.MOD = MOD
def main():
    n = int(input())
    a = list(map(int, input().split()))
    _, q = LinearRecurrence.Berlecamp_Massey(a)
    k = len(q) - 1
    coeffs = [(-q[i]) % MOD for i in range(1, k + 1)]
    coeffs.reverse()
    print(k)
    if k > 0:
        print(" ".join(map(str, coeffs)))


if __name__ == "__main__":
    main()
