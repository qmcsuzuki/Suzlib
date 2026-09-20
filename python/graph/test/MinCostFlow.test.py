# competitive-verifier: PROBLEM https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=GRL_6_B

from python.graph.MinCostFlow import MCFGraph


def main() -> None:
    n, m, f = map(int, input().split())
    graph = MCFGraph(n)
    for _ in range(m):
        u, v, cap, cost = map(int, input().split())
        graph.add_edge(u, v, cap, cost)

    flow, cost = graph.flow(0, n - 1, f)
    print(cost if flow == f else -1)


if __name__ == "__main__":
    main()
