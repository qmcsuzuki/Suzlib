# competitive-verifier: TITLE 最大二部マッチング（辺追加可能）

from python.graph.BipartiteMatching import BipartiteMatching


class DynamicBipartiteMatching:
    """BipartiteMatching の旧 API 互換ラッパー。"""

    def __init__(self, n: int, m: int) -> None:
        self.n = n
        self.m = m
        self._matching = BipartiteMatching(n, m)
        self.g = self._matching.g
        self.X2Y = self._matching.mate_left
        self.Y2X = self._matching.mate_right
        self.cnt = 0
        self._built = False

    def add_edge(self, x: int, y: int) -> None:
        """初回の max_matching より前に辺 (x, y) を追加する。"""
        if self._built:
            raise RuntimeError("use increment_edge() after max_matching()")
        self._matching.add_edge(x, y)

    def max_matching(self) -> tuple[int, list[int], list[int]]:
        """最大マッチング数と左右の対応配列を返す。"""
        self._built = True
        self.cnt = self._matching.solve()
        return self.cnt, self.X2Y, self.Y2X

    def increment_edge(self, x: int, y: int) -> bool:
        """辺 (x, y) を追加し、最大マッチング数が増えたかを返す。"""
        if not self._built:
            raise RuntimeError("call max_matching() first")
        old = self.cnt
        self._matching.add_edge(x, y)
        self.cnt = self._matching.solve()
        return self.cnt > old

    def increment_edges_from_left(self, x: int, ys: list[int]) -> bool:
        """一つの左頂点 x から複数の辺を追加し、サイズが増えたかを返す。"""
        if not self._built:
            raise RuntimeError("call max_matching() first")
        old = self.cnt
        for y in ys:
            self._matching.add_edge(x, y)
        self.cnt = self._matching.solve()
        return self.cnt > old

    def increment_edges_from_right(self, y: int, xs: list[int]) -> bool:
        """複数の左頂点から一つの右頂点 y へ辺を追加し、サイズが増えたかを返す。"""
        if not self._built:
            raise RuntimeError("call max_matching() first")
        old = self.cnt
        for x in xs:
            self._matching.add_edge(x, y)
        self.cnt = self._matching.solve()
        return self.cnt > old
