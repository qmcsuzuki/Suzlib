# competitive-verifier: TITLE 上下限・需給付き最小費用フロー

from typing import NamedTuple

from python.graph.flow.mincostflow.MinCostFlow import MCFGraph


class MinCostBFlow:
    """一般の有向グラフ上の、流出量 - 流入量 = balance を満たす最小費用流。

    正の balance は供給、負は需要。容量・需給・費用は整数。
    各辺は 0 <= lower <= flow <= upper、upper は有限。負費用・負閉路・
    自己ループ・多重辺を許す。全頂点の balance が0なら最小費用循環流。
    add_balance_range で需給を範囲 [lo, hi]（"-inf" / "inf" 可）と単位費用 cost で
    指定できる（範囲は和をとり、費用の異なる範囲を重ねると需給の区分線形凸費用になる）。
    add_balance / add_balance_range / add_edge は solve 前のみ。solve は成否によらず1回限定で、
    成功時 (True, 最小費用)、実行不能時 (False, 0) を返す。
    get_edge / edges は成功後のみ。元の辺を追加順に、元の向き・費用で返す。

    dag=False（既定）では、非負費用辺は下限、負費用辺は上限まで流した状態を
    基準にする。負費用辺は逆向き・費用 -cost の辺に置き換え、残りの需給を
    補助始点・終点間の MCFGraph で満たす。初期残余費用は全て非負。
    変換後の流量 x から、非負費用辺は lower+x、負費用辺は upper-x と復元。

    dag=True では負費用辺も反転せず、全辺を下限まで流した状態を基準にする。
    負費用辺は MCFGraph の初期ポテンシャルで扱い、上限まで流すことはない。
    正容量の負費用辺がある場合、upper > lower の辺全体が DAG であることを要し、
    閉路があれば solve で AssertionError。負閉路・負費用の自己ループは不可。
    頂点番号がトポロジカル順なら、初期ポテンシャルの計算は O(n+m) の1パス。

    n 頂点 m 辺、変換後の総供給量 D、増流回数 A<=D として、
    構築 O(n+m)、solve は sparse で O(n+m+(A+1)*(n+m+1)*log(n+m+2))、
    dense で O(n+m+(A+1)*((n+1)**2+m))。空間 O(n+m)。
    D は「指定した需給 + 基準状態の流量による需給」の正の部分の和。
    dag=False では負費用辺の upper が D に入る。dag=True では下限だけが入り、
    負費用辺の容量は D に影響しない。
    巨大容量でも1回でまとめて増流する場合はあるが、scaling は行わない。

    範囲は補助頂点 z からの辺 z→v（容量 hi-lo、費用 cost）で表す。無制限側は頂点ごとの値
    M_v = 2*(v に入る辺と出る辺の上限の和) + |v の固定の需給| + (v の範囲の有限な端点の絶対値の和)
    で置き換える（最適解を変えない十分大きい値）。同じ頂点で、hi="inf" の範囲の費用が
    別の lo="-inf" の範囲の費用より小さいと費用が下に非有界なので、solve で AssertionError。
    dag=False で cost < 0 の範囲は上限まで流した状態を基準にするため、その幅が D に入る。
    dag=True では cost < 0 の範囲（幅が正）も負費用辺として数え、upper > lower の元の辺
    全体が DAG であることを要する（z は出る辺しか持たないので新たな閉路は作らない）。
    add_balance / get_edge は O(1)、add_edge は償却 O(1)、edges は O(m)。

    使用例:
        g = MinCostBFlow(2)
        g.add_balance(0, 2)
        g.add_balance(1, -2)
        g.add_edge(0, 1, lower=1, upper=5, cost=-3)
        assert g.solve() == (True, -6)
        assert g.get_edge(0).flow == 2

        # 頂点 0 は 3 単位まで費用 1、それを超えると費用 5 で供給できる。
        g = MinCostBFlow(2)
        g.add_balance_range(0, 0, 3, cost=1)
        g.add_balance_range(0, 0, "inf", cost=5)
        g.add_balance(1, -4)
        g.add_edge(0, 1, lower=0, upper=10, cost=0)
        assert g.solve() == (True, 8) and g.balance(0) == 4
    """

    class Edge(NamedTuple):
        src: int
        dst: int
        lower: int
        upper: int
        flow: int
        cost: int

    def __init__(self, n: int, dense: bool = False, dag: bool = False) -> None:
        """n 頂点、全需給0で初期化。dense=True は密 Dijkstra を用いる。
        dag=True は負費用辺を反転せず、DAG 上の初期ポテンシャルで扱う。
        """
        assert n >= 0
        self._n = n
        self._dag = dag
        self._graph = MCFGraph(n + 2, dense=dense)
        self._balance = [0] * n
        self._ranges: list[tuple[int, int | str, int | str, int]] = []
        self._balances: list[int] = []
        self._edges: list[tuple[int, int, int, int, int]] = []
        self._initial_cost = 0
        self._solved = False
        self._feasible = False

    def add_balance(self, v: int, amount: int) -> None:
        """頂点 v の需給に amount を加える。solve 前のみ。"""
        assert not self._solved
        assert 0 <= v < self._n
        self._balance[v] += amount

    def add_balance_range(self, v: int, lo: int | str, hi: int | str, cost: int = 0) -> None:
        """頂点 v の需給に、範囲 [lo, hi] から選ぶ量 x と費用 cost * x を加える。solve 前のみ。
        lo は整数か "-inf"、hi は整数か "inf"。呼び出しごとに独立な量として足し合わせる。
        """
        assert not self._solved
        assert 0 <= v < self._n
        assert lo == "-inf" or isinstance(lo, int)
        assert hi == "inf" or isinstance(hi, int)
        assert lo == "-inf" or hi == "inf" or lo <= hi
        self._ranges.append((v, lo, hi, cost))

    def add_edge(self, src: int, dst: int, lower: int, upper: int,
                 cost: int) -> int:
        """上下限・単位費用を指定して辺を追加し、0始まりの辺番号を返す。"""
        assert not self._solved
        assert 0 <= src < self._n and 0 <= dst < self._n
        assert 0 <= lower <= upper
        if cost < 0 and not self._dag:
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
        n = self._n
        g = self._graph
        need = self._balance.copy()
        initial_cost = self._initial_cost
        if self._ranges:
            # 無制限側を頂点ごとの十分大きい値 M_v で置き換える。
            bound = [abs(b) for b in self._balance]
            for src, dst, _, upper, _ in self._edges:
                bound[src] += 2 * upper
                bound[dst] += 2 * upper
            ups = [[] for _ in range(n)]
            downs = [[] for _ in range(n)]
            for k, (v, lo, hi, cost) in enumerate(self._ranges):
                if lo == "-inf":
                    downs[v].append((cost, k))
                else:
                    bound[v] += abs(lo)
                if hi == "inf":
                    ups[v].append((cost, k))
                else:
                    bound[v] += abs(hi)
            for v in range(n):
                assert not any(cu < cd and ku != kd for cu, ku in ups[v] for cd, kd in downs[v]), \
                    "unbounded: an 'inf' range is cheaper than another '-inf' range at the same vertex"
            z = g.add_vertex()
            need += [0, 0, 0]
            for v, lo, hi, cost in self._ranges:
                lo = -bound[v] if lo == "-inf" else lo
                hi = bound[v] if hi == "inf" else hi
                # 範囲の下限 lo は v に固定で課し、残り x - lo を辺 z→v で流す。
                need[v] += lo
                initial_cost += lo * cost
                if lo == hi:
                    continue
                if cost < 0 and not self._dag:
                    # add_edge と同様、負費用は上限まで流した状態を基準にして反転する。
                    g.add_edge(v, z, hi - lo, -cost)
                    need[v] += hi - lo
                    initial_cost += (hi - lo) * cost
                else:
                    g.add_edge(z, v, hi - lo, cost)
            need[z] = -sum(need)
        elif sum(need) != 0:
            return False, 0
        source, sink = n, n + 1
        required = 0
        for v, b in enumerate(need):
            if b > 0:
                g.add_edge(source, v, b, 0)
                required += b
            elif b < 0:
                g.add_edge(v, sink, -b, 0)
        sent, cost = g.flow(source, sink, required)
        if sent != required:
            return False, 0
        self._feasible = True
        balances = [0] * n
        for e in self.edges():
            balances[e.src] += e.flow
            balances[e.dst] -= e.flow
        self._balances = balances
        return True, initial_cost + cost

    def get_edge(self, i: int) -> Edge:
        """成功後、元の辺の始終点・上下限・最適流量・費用を返す。O(1)。"""
        assert self._feasible
        assert 0 <= i < len(self._edges)
        src, dst, lower, upper, cost = self._edges[i]
        x = self._graph.get_edge(i).flow
        flow = upper - x if cost < 0 and not self._dag else lower + x
        return self.Edge(src, dst, lower, upper, flow, cost)

    def edges(self) -> list[Edge]:
        """成功後、元の辺を追加順に返す。補助辺は含めない。O(m)。"""
        assert self._feasible
        return [self.get_edge(i) for i in range(len(self._edges))]

    def potential(self) -> list[int]:
        """成功後、元の頂点の長さ n のポテンシャル p を返す。O(n)。

        元の辺で flow < upper なら cost+p[src]-p[dst] >= 0、
        flow > lower なら cost+p[src]-p[dst] <= 0 を満たす。正規化はしない。
        """
        assert self._feasible
        return self._graph.potential()[:self._n]

    def balance(self, v: int) -> int:
        """成功後、最適解での頂点 v の需給（流出量 - 流入量）を返す。O(1)。"""
        assert self._feasible
        assert 0 <= v < self._n
        return self._balances[v]
