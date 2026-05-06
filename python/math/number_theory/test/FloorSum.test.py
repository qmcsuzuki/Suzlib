# verification-helper: PROBLEM https://judge.yosupo.jp/problem/floor_sum

from python.math.number_theory.FloorSum import floor_sum
import sys
readline = sys.stdin.buffer.readline


def main():
    T = int(readline())
    for _ in range(T):
        n,m,a,b = map(int,readline().split())
        print(floor_sum(n,m,a,b))


if __name__ == '__main__':
    main()
