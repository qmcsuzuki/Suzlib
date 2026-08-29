# competitive-verifier: PROBLEM https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=GRL_6_A

from python.graph.MaxFlow import MFGraph


def main() -> None:
    n, m = map(int, input().split())
    graph = MFGraph(n)
    for _ in range(m):
        u, v, c = map(int, input().split())
        graph.add_edge(u, v, c)
    print(graph.flow(0, n - 1))


if __name__ == "__main__":
    main()
