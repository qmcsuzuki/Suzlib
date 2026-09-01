# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/bipartitematching

from python.graph.BipartiteMatching import BipartiteMatching


def main() -> None:
    L, R, M = map(int, input().split())
    matching = BipartiteMatching(L, R)
    matching.solve()

    for _ in range(M):
        a, b = map(int, input().split())
        matching.increment_edge(a, b)

    print(matching.size)
    for a, b in matching.matching_edges():
        print(a, b)


if __name__ == "__main__":
    main()
