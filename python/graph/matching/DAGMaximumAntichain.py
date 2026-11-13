# competitive-verifier: TITLE 推移閉包の二部マッチングによる最大反鎖

from python.graph.matching.BipartiteMatching import BipartiteMatching


class DAGMaximumAntichain:
    """重みなし最大反鎖。到達可能な相異なる全頂点対を add_edge する。
    solve は最大サイズ、antichain は頂点列を返す。O((n+m)√n) 時間。
    """

    def __init__(self, n: int) -> None:
        self._n = n
        self._matching = BipartiteMatching(n, n)
        self._antichain = None

    def add_edge(self, u: int, v: int) -> int:
        """DAG の辺 u→v を追加し、辺 ID を返す。solve 前のみ。"""
        if self._antichain is not None:
            raise RuntimeError("call add_edge() before solve()")
        assert 0 <= u < self._n and 0 <= v < self._n
        return self._matching.add_edge(u, v)

    def solve(self) -> int:
        """最大サイズを返す。入力は推移閉包を仮定する。1 回限定。"""
        if self._antichain is not None:
            raise RuntimeError("solve() can only be called once")
        size = self._n - self._matching.solve()
        left, right = self._matching.max_independent_set()
        in_right = set(right)
        self._antichain = [v for v in left if v in in_right]
        return size

    def antichain(self) -> list[int]:
        """solve 後、最大反鎖を頂点番号の昇順で返す。"""
        if self._antichain is None:
            raise RuntimeError("call solve() before antichain()")
        return self._antichain.copy()
