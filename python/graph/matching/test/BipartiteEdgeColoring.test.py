# competitive-verifier: PROBLEM https://atcoder.jp/contests/abc317/tasks/abc317_g

from python.graph.matching.BipartiteEdgeColoring import BipartiteEdgeColoring


def main() -> None:
    n, m = map(int, input().split())
    graph = BipartiteEdgeColoring(n, n)
    a = [list(map(int, input().split())) for _ in range(n)]
    for i, row in enumerate(a):
        for x in row:
            graph.add_edge(i, x - 1)

    graph.solve()
    result = [[0] * m for _ in range(n)]
    for i, color in enumerate(graph.edge_colors()):
        result[i // m][color] = a[i // m][i % m]
    print("Yes")
    for row in result:
        print(*row)


if __name__ == "__main__":
    main()
