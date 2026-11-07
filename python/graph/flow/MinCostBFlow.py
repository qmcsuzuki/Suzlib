# competitive-verifier: TITLE 上下限・需給付き最小費用フロー

from typing import NamedTuple

from python.graph.flow.MinCostFlow import MCFGraph


class MinCostBFlow:
    """一般の有向グラフ上の、流出量 - 流入量 = balance を満たす最小費用流。

    正の balance は供給、負は需要。容量・需給・費用は整数。
    各辺は 0 <= lower <= flow <= upper、upper は有限。負費用・負閉路・
    自己ループ・多重辺を許す。全頂点の balance が0なら最小費用循環流。
    add_balance / add_edge は solve 前のみ。solve は成否によらず1回限定で、
    成功時 (True, 最小費用)、実行不能時 (False, 0) を返す。
    get_edge / edges は成功後のみ。元の辺を追加順に、元の向き・費用で返す。

    非負費用辺は下限、負費用辺は上限まで流した状態を基準にする。
    負費用辺は逆向き・費用 -cost の辺に置き換え、残りの需給を補助始点・
    終点間の MCFGraph で満たす。初期残余費用は全て非負。
    変換後の流量 x から、非負費用辺は lower+x、負費用辺は upper-x と復元。

    n 頂点 m 辺、変換後の総供給量 D、増流回数 A<=D として、
    構築 O(n+m)、solve は sparse で O(n+m+(A+1)*(n+m+1)*log(n+m+2))、
    dense で O(n+m+(A+1)*((n+1)**2+m))。空間 O(n+m)。
    D は元の供給量とは異なり、辺の上下限にも依存する。
    巨大容量でも1回でまとめて増流する場合はあるが、scaling は行わない。
    add_balance / get_edge は O(1)、add_edge は償却 O(1)、edges は O(m)。

    使用例:
        g = MinCostBFlow(2)
        g.add_balance(0, 2)
        g.add_balance(1, -2)
        g.add_edge(0, 1, lower=1, upper=5, cost=-3)
        assert g.solve() == (True, -6)
        assert g.get_edge(0).flow == 2
    """

    class Edge(NamedTuple):
        src: int
        dst: int
        lower: int
        upper: int
        flow: int
        cost: int

    def __init__(self, n: int, dense: bool = False) -> None:
        """n 頂点、全需給0で初期化。dense=True は密 Dijkstra を用いる。"""
        assert n >= 0
        self._n = n
        self._graph = MCFGraph(n + 2, dense=dense)
        self._balance = [0] * n
        self._edges: list[tuple[int, int, int, int, int]] = []
        self._initial_cost = 0
        self._solved = False
        self._feasible = False

    def add_balance(self, v: int, amount: int) -> None:
        """頂点 v の需給に amount を加える。solve 前のみ。"""
        assert not self._solved
        assert 0 <= v < self._n
        self._balance[v] += amount

    def add_edge(self, src: int, dst: int, lower: int, upper: int,
                 cost: int) -> int:
        """上下限・単位費用を指定して辺を追加し、0始まりの辺番号を返す。"""
        assert not self._solved
        assert 0 <= src < self._n and 0 <= dst < self._n
        assert 0 <= lower <= upper
        if cost < 0:
            initial = upper
            i = self._graph.add_edge(dst, src, upper - lower, -cost)
        else:
            initial = lower
            i = self._graph.add_edge(src, dst, upper - lower, cost)
        self._edges.append((src, dst, lower, upper, cost))
        self._balance[src] -= initial
        self._balance[dst] += initial
        self._initial_cost += initial * cost
        return i

    def solve(self) -> tuple[bool, int]:
        """最小費用解を構築し (実行可能か, 費用) を返す。実行不能は (False, 0)。"""
        assert not self._solved
        self._solved = True
        if sum(self._balance) != 0:
            return False, 0
        g = self._graph
        source, sink = self._n, self._n + 1
        required = 0
        for v, b in enumerate(self._balance):
            if b > 0:
                g.add_edge(source, v, b, 0)
                required += b
            elif b < 0:
                g.add_edge(v, sink, -b, 0)
        sent, cost = g.flow(source, sink, required)
        if sent != required:
            return False, 0
        self._feasible = True
        return True, self._initial_cost + cost

    def get_edge(self, i: int) -> Edge:
        """成功後、元の辺の始終点・上下限・最適流量・費用を返す。O(1)。"""
        assert self._feasible
        assert 0 <= i < len(self._edges)
        src, dst, lower, upper, cost = self._edges[i]
        x = self._graph.get_edge(i).flow
        flow = upper - x if cost < 0 else lower + x
        return self.Edge(src, dst, lower, upper, flow, cost)

    def edges(self) -> list[Edge]:
        """成功後、元の辺を追加順に返す。補助辺は含めない。O(m)。"""
        assert self._feasible
        return [self.get_edge(i) for i in range(len(self._edges))]
