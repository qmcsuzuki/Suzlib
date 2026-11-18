# competitive-verifier: TITLE DAG の最大重み反鎖

from python.graph.flow.maxflow.DAGMinimumPathCover import DAGMinimumPathCover


class DAGMaximumAntichain(DAGMinimumPathCover):
    """solve() で最大重みを求め、antichain() で反鎖、paths() で対応するパス被覆を復元する。"""

    def __init__(self, n: int, weights: list[int] | None = None) -> None:
        super().__init__(n, disjoint=False)
        if weights is not None:
            assert len(weights) == n and all(isinstance(w, int) and w >= 0 for w in weights)
            self._weights = list(weights)

    def antichain(self) -> list[int]:
        """solve 後、最大重みを達成する反鎖の頂点列を復元する。"""
        if self._flow is None:
            raise RuntimeError("call solve() before antichain()")
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
