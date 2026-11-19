# competitive-verifier: TITLE DAG の上下限付き最小費用流

from python.graph.flow.mincostflow.MinCostBFlow import MinCostBFlow

class DAGLowerBoundMinCostFlow:
    """DAG 上の上下限付き st 最小費用流

    容量・指定流量は非負整数、費用は整数（負も可）。
    - g.solve(F): 流量 F ちょうど
    - g.flow(F): 流量 F 以下で最大・その中で費用最小
    - g.min_cost_flow(F): 流量 F 以下で費用最小・同費用なら流量最小
    flow / min_cost_flow は F を省略すると上限なし
    (実際の総流量, 最小費用)を返す、実行不能時は (-1, 0)

    使用例:
        g = DAGLowerBoundMinCostFlow(3, s=0, t=2)
        g.add_edge(0, 1, lower=2, upper=7, cost=3)
        g.add_edge(1, 2, lower=1, upper=6, cost=-4)
        assert g.solve(5) == (5, -5)
        assert [e.flow for e in g.edges()] == [5, 5]
        # 同じインスタンスでは1種類だけ呼ぶ。各用途で新しく構築する。

    各頂点 v で、流入辺の下限の和から流出辺の下限の和を引いた値を b(v) とする。
    b(s) に指定量（または上限）F を加え、b(t) から F を引いた後、正の b(v) の和を流す。
    内部では MinCostBFlow(dag=True) を使い、負費用辺を上限まで流す変換はしない。
    増流回数は F + sum(max(b(v), 0)) 以下で、負費用辺の容量には依存しない。
    """

    Edge = MinCostBFlow.Edge

    def __init__(self, n: int, s: int, t: int, dense: bool = False) -> None:
        """頂点数と始終点を指定する。dense は密 Dijkstra の選択。"""
        assert 0 <= s < n and 0 <= t < n and s != t
        self._n = n
        self._s = s
        self._t = t
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

    def solve(self, flow: int) -> tuple[int, int]:
        """指定量ちょうどで費用最小。実行不能は (-1, 0)。"""
        if flow is None:
            raise ValueError("specify flow for exact-flow solve()")
        return self._solve(0, flow)

    def flow(self, flow_limit: int | None = None) -> tuple[int, int]:
        """指定上限内で流量最大、その中で費用最小。実行不能は (-1, 0)。"""
        return self._solve(1, flow_limit)

    def min_cost_flow(self, flow_limit: int | None = None) -> tuple[int, int]:
        """指定上限内で費用最小、同費用なら流量最小。実行不能は (-1, 0)。"""
        return self._solve(2, flow_limit)

    def _solve(self, mode: int, flow_limit: int | None) -> tuple[int, int]:
        if self._used:
            raise RuntimeError("solve / flow / min_cost_flow can only be called once")
        assert flow_limit is None or flow_limit >= 0
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

        limit = flow_limit
        if limit is None:
            limit = sum(e[3] for e in self._edges if e[0] == self._s)
        if mode and rank[self._s] > rank[self._t]:
            limit = 0
        scale = limit + 1 if mode == 2 else 1
        g = MinCostBFlow(n, dense=self._dense, dag=True)
        # 元の辺を先に登録し、元の辺IDと内部の辺IDを一致させる。
        # 番号をトポロジカル順に振り直し、初期ポテンシャルを1パスで求める。
        for u, v, lower, upper, cost in self._edges:
            g.add_edge(rank[u], rank[v], lower, upper, cost * scale)
        g.add_balance(rank[self._s], limit)
        g.add_balance(rank[self._t], -limit)
        dummy = -1
        if mode and limit:
            dummy_cost = -1 if mode == 2 else (
                # 実辺の単純な残余増加路より高くし、実流量を優先する。
                sum(abs(c) for _, _, lo, hi, c in self._edges if lo < hi) + 1
            )
            dummy = g.add_edge(rank[self._s], rank[self._t], 0, limit, dummy_cost)
        feasible, _ = g.solve()
        if not feasible:
            return -1, 0
        self._edge_flow = [
            g.get_edge(i).flow for i in range(len(self._edges))
        ]
        self._feasible = True
        actual_flow = limit - (g.get_edge(dummy).flow if dummy >= 0 else 0)
        cost = sum(f * e[4] for f, e in zip(self._edge_flow, self._edges))
        return actual_flow, cost

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
