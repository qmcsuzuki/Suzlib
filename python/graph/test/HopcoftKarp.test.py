# verification-helper: PROBLEM https://judge.yosupo.jp/problem/bipartitematching

from python.graph.HopcoftKarp import HopcroftKarp


def main() -> None:
    L, R, M = map(int, input().split())
    hk = HopcroftKarp(L + R)

    for _ in range(M):
        a, b = map(int, input().split())
        hk.add_edge(a, L + b)

    size = hk.solve()
    print(size)
    for u, v in hk.matching_edges():
        if u >= L:
            u, v = v, u
        print(u, v - L)


if __name__ == "__main__":
    main()
