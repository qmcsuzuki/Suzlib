# competitive-verifier: TITLE DAG の最大重み反鎖

from python.graph.flow.maxflow.DAGMinimumPathCover import _minimum_cover_flow


class DAGMaximumAntichain:
    """元の DAG の辺と非負整数重みから最大重み反鎖を求める。
    重み省略時はすべて 1。最大流を高々2回呼び、復元は O(n+m)。
    """

    def __init__(self, n: int, weights: list[int] | None = None) -> None:
        assert n >= 0
        if weights is not None:
            assert len(weights) == n and all(isinstance(w, int) and w >= 0 for w in weights)
        self._n = n
        self._weights = [1] * n if weights is None else list(weights)
        self._edges: list[tuple[int, int]] = []
        self._antichain: list[int] | None = None

    def add_edge(self, u: int, v: int) -> int:
        """DAG の辺 u→v を追加し、辺 ID を返す。solve 前のみ。"""
        if self._antichain is not None:
            raise RuntimeError("call add_edge() before solve()")
        assert 0 <= u < self._n and 0 <= v < self._n
        self._edges.append((u, v))
        return len(self._edges) - 1

    def solve(self) -> int:
        """最大重みを返す。入力が DAG であることを仮定する。1 回限定。"""
        if self._antichain is not None:
            raise RuntimeError("solve() can only be called once")
        n = self._n
        value, graph = _minimum_cover_flow(n, self._edges, self._weights, False)
        residual = [[] for _ in range(2 * n + 2)]
        for u, v, lower, upper, flow in graph.edges():
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
        self._antichain = [v for v in range(n) if not seen[v] and seen[n + v]]
        return value

    def antichain(self) -> list[int]:
        """solve 後、最大重みを達成する反鎖を頂点番号の昇順で返す。"""
        if self._antichain is None:
            raise RuntimeError("call solve() before antichain()")
        return self._antichain.copy()
