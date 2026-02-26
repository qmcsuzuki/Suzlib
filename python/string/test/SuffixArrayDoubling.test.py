# verification-helper: PROBLEM https://judge.yosupo.jp/problem/suffixarray

from python.string.SuffixArrayDoubling import suffix_array_doubling


def main() -> None:
    s = input().strip()
    print(*suffix_array_doubling(s))


if __name__ == "__main__":
    main()
