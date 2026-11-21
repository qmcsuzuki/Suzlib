# competitive-verifier: TITLE 上下限・需給付きフロー

from typing import NamedTuple

from python.graph.flow.maxflow.MaxFlow import MFGraph


class BFlow:
    """流出量 - 流入量 = balance を満たす整数フロー。

    辺には流量下限/上限 (lower/upper) を指定できる。
    頂点には需給 balance を指定できる（正なら供給、負なら需要）。
    需給は範囲 [lo, hi] でも指定でき、"-inf" / "inf" で片側または両側を無制限にできる。
    無制限側は v に入る辺 / v から出る辺の上限の和で置き換える（辺の上限は有限）。
    solve 後は指定辺・指定頂点の需給の最適化を何度でも行える。

    範囲は補助頂点 z からの辺 z→v（容量 hi-lo）で表し、v の需給は lo + (z→v の流量)。
    solve は最大流 1 回、maximize_* / minimize_* はそれぞれ最大流 1 回。

    使用例:
        g = BFlow(3)
        g.add_balance(0, 3)   # 3供給
        g.add_balance(2, -3)  # 3需要
        g.add_edge(0, 1, 1, 4)
        g.add_edge(1, 2, 1, 4)
        e = g.add_edge(0, 2, 0, 2)
        if g.solve():
            assert g.maximize_edge(e) == 2
            assert g.minimize_edge(e) == 0

        g = BFlow(3)
        g.add_balance_range(0, 0, "inf")    # 0 以上の供給
        g.add_balance_range(2, "-inf", -1)  # 1 以上の需要
        g.add_edge(0, 1, 0, 4)
        g.add_edge(1, 2, 0, 3)
        if g.solve():
            assert g.maximize_balance(0) == 3
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
        # 需給の範囲 [lo, hi]。*_inf が True の側は無制限。
        self._lo = [0] * n
        self._hi = [0] * n
        self._lo_inf = [False] * n
        self._hi_inf = [False] * n
        # 辺の下限を先に流した分の需給の補正。
        self._shift = [0] * n
        self._lower: list[int] = []
        self._range_lo: list[int] = []
        self._range_edge: list[int] = []
        self._solved = False
        self._feasible = False

    def add_balance(self, v: int, amount: int) -> None:
        """頂点 v の需給に amount を加える。add_balance_range(v, amount, amount) と同じ。solve 前のみ。"""
        assert not self._solved
        assert 0 <= v < self._n
        self._lo[v] += amount
        self._hi[v] += amount

    def add_balance_range(self, v: int, lo: int | str, hi: int | str) -> None:
        """頂点 v の需給に範囲 [lo, hi] を加える（範囲どうしは和をとる）。solve 前のみ。
        lo は整数か "-inf"、hi は整数か "inf"。
        """
        assert not self._solved
        assert 0 <= v < self._n
        assert lo == "-inf" or isinstance(lo, int)
        assert hi == "inf" or isinstance(hi, int)
        assert lo == "-inf" or hi == "inf" or lo <= hi
        if lo == "-inf":
            self._lo_inf[v] = True
        else:
            self._lo[v] += lo
        if hi == "inf":
            self._hi_inf[v] = True
        else:
            self._hi[v] += hi

    def add_edge(self, src: int, dst: int, lower: int, upper: int) -> int:
        """上下限付き辺を追加し、0始まりの辺番号を返す。solve 前のみ。"""
        assert not self._solved
        assert 0 <= src < self._n and 0 <= dst < self._n
        assert 0 <= lower <= upper
        i = self._graph.add_edge(src, dst, upper - lower)
        self._lower.append(lower)
        self._shift[src] -= lower
        self._shift[dst] += lower
        return i

    def solve(self) -> bool:
        """実行可能解を構築する。解がなければ False。成否によらず1回限定。"""
        assert not self._solved
        self._solved = True
        n = self._n
        g = self._graph
        # 需給は [-(入る辺の上限の和), 出る辺の上限の和] に収まるので、無制限側をこれで置き換える。
        out_upper = [0] * n
        in_upper = [0] * n
        for i, lower in enumerate(self._lower):
            e = g.get_edge(i)
            out_upper[e.src] += lower + e.cap
            in_upper[e.dst] += lower + e.cap
        lo = [-in_upper[v] if self._lo_inf[v] else self._lo[v] for v in range(n)]
        hi = [out_upper[v] if self._hi_inf[v] else self._hi[v] for v in range(n)]
        if any(a > b for a, b in zip(lo, hi)):
            return False
        # 補助頂点 z から v へ容量 hi-lo の辺を張る。z の需給は全体の和を 0 にする値。
        z = g.add_vertex()
        self._range_lo = lo
        self._range_edge = [g.add_edge(z, v, b - a) if a < b else -1 for v, (a, b) in enumerate(zip(lo, hi))]
        need = [a + d for a, d in zip(lo, self._shift)] + [0, 0, -sum(lo)]
        source = n
        sink = source + 1
        auxiliary = []
        required = 0
        for v, b in enumerate(need):
            if b > 0:
                auxiliary.append(g.add_edge(source, v, b))
                required += b
            elif b < 0:
                auxiliary.append(g.add_edge(v, sink, -b))
        self._feasible = g.flow(source, sink, required) == required
        # 補助辺の順逆両方向を無効化し、以後は各頂点の需給を範囲内に保つ。
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
        """現在の解の元の辺を追加順に返す。"""
        assert self._feasible
        return [self.get_edge(i) for i in range(len(self._lower))]

    def maximize_edge(self, i: int) -> int:
        """辺 i の流量を最大化するフローを作り、その最大値を返す"""
        assert self._feasible
        assert 0 <= i < len(self._lower)
        return self._lower[i] + self._graph.increase_edge(i)

    def minimize_edge(self, i: int) -> int:
        """辺 i の流量を最小化するフローを作り、その最小値を返す"""
        assert self._feasible
        assert 0 <= i < len(self._lower)
        return self._lower[i] + self._graph.decrease_edge(i)

    def balance(self, v: int) -> int:
        """現在の解での頂点 v の需給（流出量 - 流入量）を返す。成功後のみ。"""
        assert self._feasible
        assert 0 <= v < self._n
        i = self._range_edge[v]
        return self._range_lo[v] + (self._graph.get_edge(i).flow if i >= 0 else 0)

    def maximize_balance(self, v: int) -> int:
        """頂点 v の需給を範囲内で最大化するフローを作り、その最大値を返す"""
        assert self._feasible
        assert 0 <= v < self._n
        i = self._range_edge[v]
        return self._range_lo[v] + (self._graph.increase_edge(i) if i >= 0 else 0)

    def minimize_balance(self, v: int) -> int:
        """頂点 v の需給を範囲内で最小化するフローを作り、その最小値を返す"""
        assert self._feasible
        assert 0 <= v < self._n
        i = self._range_edge[v]
        return self._range_lo[v] + (self._graph.decrease_edge(i) if i >= 0 else 0)
