# competitive-verifier: PROBLEM https://atcoder.jp/contests/practice2/tasks/practice2_e

from python.graph.MinCostFlow import DAGMCFGraph


def main() -> None:
    n, k = map(int, input().split())
    a = [list(map(int, input().split())) for _ in range(n)]

    s = 2 * n
    t = s + 1
    graph = DAGMCFGraph(2 * n + 2, s, t)

    for i in range(n):
        graph.add_edge(s, i, k, 0)
    for j in range(n):
        graph.add_edge(n + j, t, k, 0)

    edge_id = [[-1] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            edge_id[i][j] = graph.add_edge(i, n + j, 1, -a[i][j])

    graph.add_edge(s, t, n * k, 0)
    _, cost = graph.flow(n * k)
    print(-cost)

    for i in range(n):
        row = []
        for j in range(n):
            row.append("X" if graph.get_edge(edge_id[i][j]).flow else ".")
        print("".join(row))


if __name__ == "__main__":
    main()
