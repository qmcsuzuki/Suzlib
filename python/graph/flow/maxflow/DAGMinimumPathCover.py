# competitive-verifier: TITLE 下限付き最小流による DAG の最小パス被覆

from python.graph.flow.maxflow.LowerBoundSTFlow import LowerBoundSTFlow
from python.graph.topological_sort import topological_sort


def _minimum_cover_flow(n, edges, lower, disjoint):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    if topological_sort(adj) is None:
        raise ValueError("graph must be a DAG")
    s, t = 2 * n, 2 * n + 1
    # 各頂点を単独で覆う解より大きく取り、最小流で上限が効かないようにする。
    upper = sum(lower) + 1
    g = LowerBoundSTFlow(t + 1, s, t)
    for v, demand in enumerate(lower):
        g.add_edge(s, v, 0, upper)
        g.add_edge(v, n + v, demand, 1 if disjoint else upper)
        g.add_edge(n + v, t, 0, upper)
    for u, v in edges:
        g.add_edge(n + u, v, 0, upper)
    if not g.solve():
        raise RuntimeError("singleton paths must form a feasible cover")
    return g.minimize(), g


class DAGMinimumPathCover:
    """元の DAG の辺で全頂点を覆う最小本数とパス列。
    disjoint=True で点素、False で頂点共有可。単頂点パスも許す。
    solve は下限付き最小流（最大流を高々2回）。復元は O(n+m+出力長)。
    """

    def __init__(self, n: int, *, disjoint: bool = True) -> None:
        assert n >= 0
        self._n = n
        self._disjoint = disjoint
        self._edges = []
        self._used = False
        self._flow = None

    def add_edge(self, u: int, v: int) -> int:
        if self._used:
            raise RuntimeError("call add_edge() before solve()")
        assert 0 <= u < self._n and 0 <= v < self._n
        self._edges.append((u, v))
        return len(self._edges) - 1

    def solve(self) -> int:
        if self._used:
            raise RuntimeError("solve() can only be called once")
        self._used = True
        count, self._flow = _minimum_cover_flow(
            self._n, self._edges, [1] * self._n, self._disjoint)
        return count

    def _paths(self, edge_ids):
        if self._flow is None:
            raise RuntimeError("call solve() before paths()")
        n = self._n
        outgoing = [[] for _ in range(n)]
        remaining = []
        for i, (u, v) in enumerate(self._edges):
            amount = self._flow.get_edge(3 * n + i).flow
            remaining.append(amount)
            if amount:
                outgoing[u].append(i)
        paths = []
        for start in range(n):
            for _ in range(self._flow.get_edge(3 * start).flow):
                u = start
                path = [] if edge_ids else [u]
                while outgoing[u]:
                    i = outgoing[u][-1]
                    remaining[i] -= 1
                    if not remaining[i]:
                        outgoing[u].pop()
                    u = self._edges[i][1]
                    path.append(i if edge_ids else u)
                paths.append(path)
        return paths

    def paths(self) -> list[list[int]]:
        return self._paths(False)

    def edge_paths(self) -> list[list[int]]:
        return self._paths(True)
