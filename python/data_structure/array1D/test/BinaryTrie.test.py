# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/set_xor_min

import sys
from python.data_structure.array1D.BinaryTrie import BinaryTrie

readline = sys.stdin.readline


def main() -> None:
    q = int(readline())
    bt = BinaryTrie(max_bit=29)

    for _ in range(q):
        t, x = map(int, readline().split())
        if t == 0:
            if bt.count(x) == 0:
                bt.add(x)
        elif t == 1:
            bt.discard(x)
        else:
            print(bt.min_xor_value(x))


if __name__ == '__main__':
    main()
