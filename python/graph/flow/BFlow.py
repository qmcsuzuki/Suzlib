# competitive-verifier: TITLE 上下限・需給付きフロー

from typing import NamedTuple

from python.graph.flow.MaxFlow import MFGraph


class BFlow:
    """流出量 - 流入量 = balance を満たす整数フロー。

    正の balance は供給、負は需要。辺は 0 <= lower <= flow <= upper。
    solve は1回だけ呼べる。成功後は指定辺の最適化を何度でも行える。
    solve と各最適化は最大流を高々1回呼ぶ。一般に O(V^2 (E+V)) 時間、
    O(V+E) 空間。前回最適化した辺の流量は固定しない。
    全頂点の balance が0なら上下限付き循環流。自己ループ・多重辺も扱える。
    辺・需給の追加は solve 前、最適化・解の取得は solve 成功後のみ。
    get_edge は O(1)、edges は O(E)。補助辺は含めず、下限を足し戻した
    src, dst, lower, upper, flow を返す。取得済みの値は後の最適化で変わらない。

    使用例:
        g = BFlow(3)
        g.add_balance(0, 3)   # 3供給
        g.add_balance(2, -3)  # 3需要
        g.add_edge(0, 1, 1, 4)
        g.add_edge(1, 2, 1, 4)
        e = g.add_edge(0, 2, 0, 2)
        if g.solve():
            assert g.maximize_edge(e) == 2
            maximum_edges = g.edges()
            assert g.minimize_edge(e) == 0
            minimum_edges = g.edges()
    """

    class Edge(NamedTuple):
        src: int
        dst: int
        lower: int
        upper: int
        flow: int

    def __init__(self, n: int) -> None:
        """n 頂点、全頂点の需給0で初期化する。"""
        assert n >= 0
        self._n = n
        self._graph = MFGraph(n + 2)
        self._balance = [0] * n
        self._lower: list[int] = []
        self._solved = False
        self._feasible = False

    def add_balance(self, v: int, amount: int) -> None:
        """頂点 v の需給に amount を加える。solve 前のみ。"""
        assert not self._solved
        assert 0 <= v < self._n
        self._balance[v] += amount

    def add_edge(self, src: int, dst: int, lower: int, upper: int) -> int:
        """上下限付き辺を追加し、0始まりの辺番号を返す。solve 前のみ。"""
        assert not self._solved
        assert 0 <= src < self._n and 0 <= dst < self._n
        assert 0 <= lower <= upper
        i = self._graph.add_edge(src, dst, upper - lower)
        self._lower.append(lower)
        self._balance[src] -= lower
        self._balance[dst] += lower
        return i

    def solve(self) -> bool:
        """実行可能解を構築する。解がなければ False。成否によらず1回限定。

        下限を需給へ移し、補助始点・終点間の最大流で判定する。
        補助辺は判定後に順逆とも無効化する。
        """
        assert not self._solved
        self._solved = True
        if sum(self._balance) != 0:
            return False
        g = self._graph
        source = self._n
        sink = source + 1
        auxiliary = []
        required = 0
        for v, b in enumerate(self._balance):
            if b > 0:
                auxiliary.append(g.add_edge(source, v, b))
                required += b
            elif b < 0:
                auxiliary.append(g.add_edge(v, sink, -b))
        self._feasible = g.flow(source, sink, required) == required
        # 補助辺の順逆両方向を無効化し、以後は元の頂点の需給を保つ。
        for i in auxiliary:
            g.change_edge(i, 0, 0)
        return self._feasible

    def get_edge(self, i: int) -> Edge:
        """現在の解の元の辺を返す。下限を足し戻した独立な値。成功後のみ。"""
        assert self._feasible
        assert 0 <= i < len(self._lower)
        e = self._graph.get_edge(i)
        lower = self._lower[i]
        return BFlow.Edge(e.src, e.dst, lower, lower + e.cap, lower + e.flow)

    def edges(self) -> list[Edge]:
        """現在の解の元の辺を追加順に返す。O(E)。成功後のみ。"""
        assert self._feasible
        return [self.get_edge(i) for i in range(len(self._lower))]

    def _optimize_edge(self, i: int, maximize: bool) -> int:
        """対象辺 u→v を除き、増加時は v→u、減少時は u→v に残余流を流す。

        対象辺を同量だけ増減すると差分が循環流になり、需給を保つ。
        任意の実行可能解との差もこの形で表せるため最適値を得る。
        自己ループは需給に影響せず直接上下限に設定する。
        """
        assert self._feasible
        assert 0 <= i < len(self._lower)
        g = self._graph
        e = g.get_edge(i)
        limit = e.cap - e.flow if maximize else e.flow
        if e.src == e.dst:
            delta = limit
        else:
            # 対象辺自身の逆辺を使った見かけの増減を禁止する。
            g.change_edge(i, 0, 0)
            if maximize:
                delta = g.flow(e.dst, e.src, limit)
            else:
                delta = g.flow(e.src, e.dst, limit)
        flow = e.flow + delta if maximize else e.flow - delta
        g.change_edge(i, e.cap, flow)
        return self._lower[i] + flow

    def maximize_edge(self, i: int) -> int:
        """辺 i の流量を最大化し、増分ではなく最大値を返す。解も更新する。"""
        return self._optimize_edge(i, True)

    def minimize_edge(self, i: int) -> int:
        """辺 i の流量を最小化し、減少量ではなく最小値を返す。解も更新する。"""
        return self._optimize_edge(i, False)
