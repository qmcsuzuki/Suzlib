# competitive-verifier: TITLE 推移閉包の二部マッチングによる最大反鎖

from python.graph.matching.BipartiteMatching import BipartiteMatching


class DAGMaximumAntichain:
    """重みなし最大反鎖を O((n+m)√n) 時間で求める。
    add_edge した辺が推移閉包をなすことが前提
    solve は最大サイズと反鎖の頂点列を返す。
    """

    def __init__(self, n: int) -> None:
        self._n = n
        self._matching = BipartiteMatching(n, n)
        self._solved = False

    def add_edge(self, u: int, v: int) -> int:
        """DAG の辺 u→v を追加し、辺 ID を返す。solve 前のみ。"""
        if self._solved:
            raise RuntimeError("call add_edge() before solve()")
        assert 0 <= u < self._n and 0 <= v < self._n
        return self._matching.add_edge(u, v)

    def solve(self) -> tuple[int, list[int]]:
        """最大サイズと反鎖の頂点列を返す。入力は推移閉包を仮定する。1 回限定。"""
        if self._solved:
            raise RuntimeError("solve() can only be called once")
        size = self._n - self._matching.solve()
        left, right = self._matching.max_independent_set()
        in_right = set(right)
        self._solved = True
        return size, [v for v in left if v in in_right]
