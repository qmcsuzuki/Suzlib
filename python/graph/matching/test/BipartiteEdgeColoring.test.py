# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/bipartite_edge_coloring

from python.graph.matching.BipartiteEdgeColoring import BipartiteEdgeColoring


def main() -> None:
    l, r, m = map(int, input().split())
    g = BipartiteEdgeColoring(l, r)
    for _ in range(m):
        u, v = map(int, input().split())
        g.add_edge(u, v)

    print(g.solve())
    print(*g.edge_colors(), sep="\n")


if __name__ == "__main__":
    main()
