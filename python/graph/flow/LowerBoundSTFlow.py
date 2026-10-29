# competitive-verifier: TITLE 下限付き s-t フロー

from python.graph.flow.BFlow import BFlow


class LowerBoundSTFlow:
    """非負の s-t 流量を持つ上下限付きフロー。BFlow の薄いラッパー。

    solve は1回限定。成功後は maximize/minimize を何度でも呼べる。
    総流量は s の流出量 - 流入量。負の総流量しか実現できなければ解なし。
    整数容量を前提とし、辺は 0 <= lower <= flow <= upper。
    辺の追加は solve 前、最適化・解の取得は solve 成功後のみ。
    総流量の指定範囲は最適化でも維持する。
    t→s の補助辺を BFlow に追加し、その辺を最適化する。
    solve と各最適化は最大流を高々1回呼び、一般に O(V^2 (E+V)) 時間、
    O(V+E) 空間。get_edge は O(1)、edges は O(E)。
    辺情報は src, dst, lower, upper, flow。補助辺は含めず、
    取得済みの値は後の最適化で変わらない。

    使用例:
        g = LowerBoundSTFlow(3, s=0, t=2)
        g.add_edge(0, 1, 1, 4)
        g.add_edge(1, 2, 1, 3)
        g.add_edge(0, 2, 0, 2)
        if g.solve():
            assert g.maximize() == 5
            max_edges = g.edges()
            assert g.minimize() == 1
            min_edges = g.edges()

    solve(flow_lower=2, flow_upper=5) で総流量を2以上5以下に制限し、
    solve(flow_lower=3, flow_upper=3) で3に固定できる。
    """

    Edge = BFlow.Edge

    def __init__(self, n: int, s: int, t: int) -> None:
        """n 頂点と始点 s、終点 t を固定する。"""
        assert 0 <= s < n and 0 <= t < n and s != t
        self._graph = BFlow(n)
        self._s = s
        self._t = t
        self._edge_count = 0
        self._source_upper = 0
        self._return_edge = -1

    def add_edge(self, src: int, dst: int, lower: int, upper: int) -> int:
        """元の辺を追加し、辺番号を返す。solve 前のみ。"""
        assert self._return_edge == -1
        i = self._graph.add_edge(src, dst, lower, upper)
        self._edge_count += 1
        if src == self._s and dst != self._s:
            self._source_upper += upper
        return i

    def solve(self, flow_lower: int = 0, flow_upper: int | None = None) -> bool:
        """総流量を指定範囲に制限し実行可能解を構築する。解なしは False。

        flow_upper=None は上限指定なし。両端を同じ値にすれば流量を固定できる。
        s から出る辺の上限の和を有限の安全な上限として用いる。
        """
        assert self._return_edge == -1
        assert flow_lower >= 0
        if flow_upper is None:
            flow_upper = max(flow_lower, self._source_upper)
        assert flow_lower <= flow_upper
        self._return_edge = self._graph.add_edge(
            self._t, self._s, flow_lower, flow_upper,
        )
        return self._graph.solve()

    def maximize(self) -> int:
        """総流量を最大化し、その値を返す。現在の解も更新する。成功後のみ。"""
        return self._graph.maximize_edge(self._return_edge)

    def minimize(self) -> int:
        """総流量を最小化し、その値を返す。現在の解も更新する。成功後のみ。"""
        return self._graph.minimize_edge(self._return_edge)

    def get_edge(self, i: int) -> Edge:
        """現在の解の元の辺を返す。補助辺は公開しない。成功後のみ。"""
        assert 0 <= i < self._edge_count
        return self._graph.get_edge(i)

    def edges(self) -> list[Edge]:
        """現在の解の元の辺だけを追加順に返す。O(E)。成功後のみ。"""
        assert self._graph._feasible
        return [self.get_edge(i) for i in range(self._edge_count)]
