# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/bipartitematching

from python.graph.matching.GeneralBipartiteMatching import GeneralBipartiteMatching


def main() -> None:
    # 左 a を a、右 b を L + b として一つの番号空間で与える。
    L, R, M = map(int, input().split())
    matching = GeneralBipartiteMatching(L + R)
    for _ in range(M):
        a, b = map(int, input().split())
        matching.add_edge(a, L + b)

    print(matching.solve())
    for u, v in matching.matching_edges():
        if u >= L:
            u, v = v, u
        print(u, v - L)


if __name__ == "__main__":
    main()
