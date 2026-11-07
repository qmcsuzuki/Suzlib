# competitive-verifier: TITLE DAG の上下限付き固定流量最小費用流

from typing import NamedTuple

from python.graph.flow.MinCostFlow import DAGMCFGraph


class DAGLowerBoundMinCostFlow:
    """DAG 上で、各辺の上下限を守り s から t へちょうど flow 流す最小費用流。

    頂点番号は任意の 0..n-1。容量・指定流量は非負整数、費用は負も可。
    多重辺を許す。自己ループを含む閉路は容量0の辺も含めて拒否する。
    solve は1回限定。成功時 (指定流量, 最小費用)、実行不能時 (-1, 0)。
    総流量の最大化や、総流量自体を選ぶ最適化は行わない。

    使用例:
        g = DAGLowerBoundMinCostFlow(3, s=0, t=2, flow=5)
        g.add_edge(0, 1, lower=2, upper=7, cost=3)
        g.add_edge(1, 2, lower=1, upper=6, cost=-4)
        assert g.solve() == (5, -5)
        assert [e.flow for e in g.edges()] == [5, 5]

    通常の DAGMCFGraph へ直接帰着する。超始点 S、超終点 T を追加し、
    S→s と t→T に容量 F を張る。元の辺 u→v (下限 l、上限 h、費用 c) は
    容量 h-l・費用 c の辺と、容量 l・費用0の S→v, u→T に置き換える。
    F+sum(l) 単位流せば補助辺が全て飽和する。元の流量は l を足し戻し、
    費用には sum(l*c) を足す。初期ネットワークは DAG のまま。

    n 頂点 m 辺、D=F+sum(l)、増流回数 A<=D として、構築 O(n+m)。
    solve は sparse で O(n+m+(A+1)*(n+m+1)*log(n+m+2))、
    dense で O(n+m+(A+1)*((n+1)**2+m))。空間 O(n+m)。
    D は指定流量 F と異なり、巨大容量は1回の増流でまとめて流す場合もある。
    get_edge は O(1)、edges は O(m)。成功後のみ取得可、補助辺は含めない。
    """

    class Edge(NamedTuple):
        src: int
        dst: int
        lower: int
        upper: int
        flow: int
        cost: int

    def __init__(self, n: int, s: int, t: int, flow: int,
                 dense: bool = False) -> None:
        """頂点数、始終点、固定総流量を指定する。dense は密 Dijkstra の選択。"""
        assert 0 <= s < n and 0 <= t < n and s != t
        assert flow >= 0
        self._n = n
        self._s = s
        self._t = t
        self._flow = flow
        self._dense = dense
        self._edges: list[tuple[int, int, int, int, int]] = []
        self._edge_flow: list[int] = []
        self._used = False
        self._feasible = False

    def add_edge(self, src: int, dst: int, lower: int, upper: int,
                 cost: int) -> int:
        """上下限・単位費用を指定して辺を追加し、辺IDを返す。solve 前のみ。償却O(1)。"""
        if self._used:
            raise RuntimeError("call add_edge() before solve()")
        assert 0 <= src < self._n and 0 <= dst < self._n
        assert 0 <= lower <= upper
        i = len(self._edges)
        self._edges.append((src, dst, lower, upper, cost))
        return i

    def solve(self) -> tuple[int, int]:
        """成功時 (指定流量, 最小費用)、実行不能時 (-1, 0)。閉路は ValueError。"""
        if self._used:
            raise RuntimeError("solve() can only be called once")
        self._used = True
        n = self._n
        adj = [[] for _ in range(n)]
        indegree = [0] * n
        for u, v, _, _, _ in self._edges:
            adj[u].append(v)
            indegree[v] += 1
        order = [v for v in range(n) if indegree[v] == 0]
        for u in order:
            for v in adj[u]:
                indegree[v] -= 1
                if indegree[v] == 0:
                    order.append(v)
        if len(order) != n:
            raise ValueError("graph must be a DAG")
        rank = [0] * n
        for i, v in enumerate(order):
            rank[v] = i

        source, sink = n, n + 1
        g = DAGMCFGraph(n + 2, source, sink, dense=self._dense)
        # 元の辺を先に登録し、元の辺IDと内部の辺IDを一致させる。
        base_cost = 0
        demand = self._flow
        for u, v, lower, upper, cost in self._edges:
            g.add_edge(rank[u], rank[v], upper - lower, cost)
            base_cost += lower * cost
            demand += lower
        g.add_edge(source, rank[self._s], self._flow, 0)
        g.add_edge(rank[self._t], sink, self._flow, 0)
        for u, v, lower, _, _ in self._edges:
            if lower:
                g.add_edge(source, rank[v], lower, 0)
                g.add_edge(rank[u], sink, lower, 0)
        sent, cost = g.flow(demand)
        if sent != demand:
            return -1, 0
        self._edge_flow = [
            e[2] + g.get_edge(i).flow for i, e in enumerate(self._edges)
        ]
        self._feasible = True
        return self._flow, base_cost + cost

    def get_edge(self, i: int) -> Edge:
        """成功後、元の頂点番号・上下限・流量・費用を返す。O(1)。"""
        if not self._feasible:
            raise RuntimeError("call solve() and check feasibility before get_edge()")
        assert 0 <= i < len(self._edges)
        u, v, lower, upper, cost = self._edges[i]
        return self.Edge(u, v, lower, upper, self._edge_flow[i], cost)

    def edges(self) -> list[Edge]:
        """成功後、元の辺を追加順に返す。O(m)。"""
        if not self._feasible:
            raise RuntimeError("call solve() and check feasibility before edges()")
        return [self.get_edge(i) for i in range(len(self._edges))]
