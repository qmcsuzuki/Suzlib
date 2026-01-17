# verification-helper: PROBLEM https://judge.yosupo.jp/problem/kth_term_of_linearly_recurrent_sequence
import python.polynomial.LinearRecurrence as LinearRecurrence

MOD = 998244353
LinearRecurrence.MOD = MOD


def main():
    k, n = map(int, input().split())
    a = list(map(int, input().split()))
    c = list(map(int, input().split()))
    g = [1] + [(-ci) % MOD for ci in c]
    ans = LinearRecurrence.rec_nth_term(a, g, n)
    print(ans)


if __name__ == "__main__":
    main()
