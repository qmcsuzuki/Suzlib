# competitive-verifier: TITLE 下限付き最小流による DAG の最小パス被覆と最大重み反鎖

from python.graph.flow.maxflow.LowerBoundSTFlow import LowerBoundSTFlow
from python.graph.topological_sort import topological_sort


def _minimum_cover_flow(n, edges, lower, disjoint):
    """各頂点の被覆回数の下限を満たす最小流量と求解済みのグラフを返す。"""
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
    頂点共有を許す場合は、同じ解から最大反鎖も復元できる。
    solve は下限付き最小流（最大流を高々2回）。復元は O(n+m+出力長)。
    """

    def __init__(self, n: int, *, disjoint: bool = True) -> None:
        """n 頂点の DAG を初期化し、disjoint=True ならパス間の頂点共有を禁止する。"""
        assert n >= 0
        self._weights = [1] * n
        self._n = n
        self._disjoint = disjoint
        self._edges = []
        self._used = False
        self._flow = None

    def add_edge(self, u: int, v: int) -> int:
        """solve 前に辺 u→v を追加し、0 始まりの辺番号を返す。"""
        if self._used:
            raise RuntimeError("call add_edge() before solve()")
        assert 0 <= u < self._n and 0 <= v < self._n
        self._edges.append((u, v))
        return len(self._edges) - 1

    def solve(self) -> int:
        """全頂点を覆うパスの最小本数を返す。呼び出しは1回限り。"""
        if self._used:
            raise RuntimeError("solve() can only be called once")
        self._used = True
        count, self._flow = _minimum_cover_flow(
            self._n, self._edges, self._weights, self._disjoint)
        return count

    def _paths(self, edge_ids):
        """求解済みのフローから各パスを復元し、edge_ids に応じて辺番号列または頂点列で返す。"""
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
        """solve 後、最小パス被覆の各パスを頂点列で返す。"""
        return self._paths(False)

    def edge_paths(self) -> list[list[int]]:
        """solve 後、最小パス被覆の各パスを辺番号列で返す。単頂点パスは空リストになる。"""
        return self._paths(True)

    def antichain(self) -> list[int]:
        """solve 後、最大重みを達成する反鎖の頂点列を復元する。"""
        if self._flow is None:
            raise RuntimeError("call solve() before antichain()")
        if self._disjoint:
            raise ValueError("antichain() requires disjoint=False")
        n = self._n
        residual = [[] for _ in range(2 * n + 2)]
        for u, v, lower, upper, flow in self._flow.edges():
            if flow < upper:
                residual[u].append(v)
            if flow > lower:
                residual[v].append(u)
        # t から到達できる側へ入る頂点分割辺は下限に一致する。
        # 元の DAG の辺と分割辺は順方向に残るため、これらの頂点は反鎖をなす。
        t = 2 * n + 1
        seen = [False] * len(residual)
        seen[t] = True
        stack = [t]
        while stack:
            u = stack.pop()
            for v in residual[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
        return [v for v in range(n) if not seen[v] and seen[n + v]]
