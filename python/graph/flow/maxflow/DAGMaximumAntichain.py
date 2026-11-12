# competitive-verifier: TITLE DAG の最大重み反鎖

from python.graph.flow.maxflow.MaxFlow import MFGraph
from python.graph.matching.BipartiteMatching import BipartiteMatching


class DAGMaximumAntichain:
    """DAG 上で、互いに到達できない頂点集合の重み和を最大化する。

    weights は非負整数の列。省略時は全頂点の重みを 1 とする。
    transitive=True は、到達可能な相異なる全頂点対が辺として
    与えられることを呼び出し側が保証する指定。
    重み省略かつ transitive=True なら二部マッチングで O((n+m)√n) 時間。
    それ以外は 2n+2 頂点、3n+m 辺の最大流を 1 回解く。空間は O(n+m)。

    使用例:
        g = DAGMaximumAntichain(n, weights)
        for u, v in edges:
            g.add_edge(u, v)
        value = g.solve()
        vertices = g.antichain()
    """

    def __init__(self, n: int, weights: list[int] | None = None, *,
                 transitive: bool = False) -> None:
        assert n >= 0
        if weights is not None:
            assert len(weights) == n and all(isinstance(w, int) and w >= 0 for w in weights)
        self._n = n
        self._weights = None if weights is None else list(weights)
        self._transitive = transitive
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
        weights = self._weights
        if weights is None and self._transitive:
            matching = BipartiteMatching(n, n)
            for u, v in self._edges:
                matching.add_edge(u, v)
            size = n - matching.solve()
            left, right = matching.max_independent_set()
            in_right = set(right)
            self._antichain = [v for v in left if v in in_right]
            return size

        if weights is None:
            weights = [1] * n
        total = sum(weights)
        inf = total + 1
        s = 2 * n
        t = s + 1
        graph = MFGraph(t + 1)
        for v, w in enumerate(weights):
            graph.add_edge(s, v, w)
            graph.add_edge(n + v, t, w)
            graph.add_edge(n + v, v, inf)
        for u, v in self._edges:
            graph.add_edge(u, n + v, inf)
        value = total - graph.flow(s, t)
        side = graph.min_cut(s)
        self._antichain = [v for v in range(n) if side[v] and not side[n + v]]
        return value

    def antichain(self) -> list[int]:
        """solve 後、最大重みを達成する反鎖を頂点番号の昇順で返す。"""
        if self._antichain is None:
            raise RuntimeError("call solve() before antichain()")
        return self._antichain.copy()
