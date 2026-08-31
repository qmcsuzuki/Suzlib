# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/bipartitematching

from python.graph.BipartiteMatching import BipartiteMatching


def main() -> None:
    L, R, M = map(int, input().split())
    matching = BipartiteMatching(L, R)
    for _ in range(M):
        a, b = map(int, input().split())
        matching.add_edge(a, b)

    print(matching.solve())
    for a, b in matching.matching_edges():
        print(a, b)


if __name__ == "__main__":
    main()
