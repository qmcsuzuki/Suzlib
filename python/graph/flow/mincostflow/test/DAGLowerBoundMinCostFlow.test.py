# competitive-verifier: PROBLEM https://atcoder.jp/contests/bogosortcontest_div2/tasks/bogosortcontest_div2_g

from python.graph.flow.mincostflow.DAGLowerBoundMinCostFlow import DAGLowerBoundMinCostFlow


def main() -> None:
    n, k, lower, upper = map(int, input().split())
    targets = list(map(int, input().split()))
    counts = list(map(int, input().split()))
    m = sum(counts)
    source, sink = 0, m + n + 4
    g = DAGLowerBoundMinCostFlow(sink + 1, source, sink, flow=n)
    i = 0
    for author, count in enumerate(counts, 1):
        g.add_edge(source, author, lower, upper, 0)
        for _ in range(count):
            difficulty, preference = map(int, input().split())
            problem = 4 + i
            g.add_edge(author, problem, 0, 1, -preference)
            for j, target in enumerate(targets):
                if abs(difficulty - target) <= k:
                    g.add_edge(problem, 4 + m + j, 0, 1, 0)
            i += 1
    for j in range(n):
        g.add_edge(4 + m + j, sink, 0, 1, 0)
    flow, cost = g.solve()
    print(-cost if flow != -1 else -1)


if __name__ == "__main__":
    main()
