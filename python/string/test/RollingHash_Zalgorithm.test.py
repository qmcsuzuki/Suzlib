# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/zalgorithm
import sys
from python.string.RollingHash import RollingHash61

readline = sys.stdin.readline


def main():
    s = readline().strip()
    n = len(s)

    rh = RollingHash61(s)
    ans = [rh.common_prefix_length(0, n, rh, i, n) for i in range(n)]
    print(*ans)


if __name__ == "__main__":
    main()
