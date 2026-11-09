# competitive-verifier: TITLE DAG の上下限付き最小費用流

from typing import NamedTuple

from python.graph.flow.mincostflow.MinCostFlow import DAGMCFGraph


class DAGLowerBoundMinCostFlow:
    """DAG 上で、各辺の上下限を守る s-t 最小費用流。

    頂点番号は任意の 0..n-1。容量・指定流量は非負整数、費用は整数（負も可）。
    多重辺を許す。自己ループを含む閉路は容量0の辺も含めて拒否する。
    solve / flow / min_cost_flow は合わせて1回限定。
    solve: 指定量ちょうど、flow: 上限内で流量最大・その中で費用最小、
    min_cost_flow: 上限内で費用最小・同費用なら流量最小。
    成功時 (実際の総流量, 最小費用)、実行不能時 (-1, 0)。
    コンストラクタの flow は solve では指定量、他の2つでは上限。
    None は上限なし（s から出る辺の上限和を使用）。solve には整数指定が必要。

    使用例:
        g = DAGLowerBoundMinCostFlow(3, s=0, t=2, flow=5)
        g.add_edge(0, 1, lower=2, upper=7, cost=3)
        g.add_edge(1, 2, lower=1, upper=6, cost=-4)
        assert g.solve() == (5, -5)
        assert [e.flow for e in g.edges()] == [5, 5]
        # 同じインスタンスでは1種類だけ呼ぶ。各用途で新しく構築する。
        # g.solve()          : ちょうど5
        # g.flow()           : 5以下で流量最大、その中で費用最小
        # g.min_cost_flow()  : 5以下で費用最小、同費用なら流量最小
        # 上限なしは DAGLowerBoundMinCostFlow(n, s, t) として後者2つを使う。

    通常の DAGMCFGraph へ直接帰着する。超始点 S、超終点 T を追加し、
    S→s と t→T に容量 F を張る。元の辺 u→v (下限 l、上限 h、費用 c) は
    容量 h-l・費用 c の辺と、容量 l・費用0の S→v, u→T に置き換える。
    F+sum(l) 単位流せば補助辺が全て飽和する。元の流量は l を足し戻し、
    費用には sum(l*c) を足す。初期ネットワークは DAG のまま。

    流量可変では容量 F の s→t ダミー辺で未使用分を流す。
    flow はダミー費用 sum((h-l)*abs(c))+1 で実流量を優先する。
    min_cost_flow は元費用を F+1 倍、ダミー費用を -1 とし同費用なら実流量最小。
    t が s よりトポロジカル順で先なら正の s-t 流は存在せず、可変時は F=0。
    返す費用は元の辺流量から計算する。

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

    def __init__(self, n: int, s: int, t: int, flow: int | None = None,
                 dense: bool = False) -> None:
        """頂点数、始終点、指定量または上限を指定する。dense は密 Dijkstra の選択。"""
        assert 0 <= s < n and 0 <= t < n and s != t
        assert flow is None or flow >= 0
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
        """指定量ちょうどで費用最小。flow=None は ValueError。実行不能は (-1, 0)。"""
        if self._flow is None:
            raise ValueError("specify flow for exact-flow solve()")
        return self._solve(0)

    def flow(self) -> tuple[int, int]:
        """指定上限内で流量最大、その中で費用最小。実行不能は (-1, 0)。"""
        return self._solve(1)

    def min_cost_flow(self) -> tuple[int, int]:
        """指定上限内で費用最小、同費用なら流量最小。実行不能は (-1, 0)。"""
        return self._solve(2)

    def _solve(self, mode: int) -> tuple[int, int]:
        if self._used:
            raise RuntimeError("solve / flow / min_cost_flow can only be called once")
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

        limit = self._flow
        if limit is None:
            limit = sum(e[3] for e in self._edges if e[0] == self._s)
        if mode and rank[self._s] > rank[self._t]:
            limit = 0
        scale = limit + 1 if mode == 2 else 1
        source, sink = n, n + 1
        g = DAGMCFGraph(n + 2, source, sink, dense=self._dense)
        # 元の辺を先に登録し、元の辺IDと内部の辺IDを一致させる。
        demand = limit
        for u, v, lower, upper, cost in self._edges:
            g.add_edge(rank[u], rank[v], upper - lower, cost * scale)
            demand += lower
        g.add_edge(source, rank[self._s], limit, 0)
        g.add_edge(rank[self._t], sink, limit, 0)
        for u, v, lower, _, _ in self._edges:
            if lower:
                g.add_edge(source, rank[v], lower, 0)
                g.add_edge(rank[u], sink, lower, 0)
        dummy = -1
        if mode and limit:
            dummy_cost = -1 if mode == 2 else (
                sum((hi - lo) * abs(c) for _, _, lo, hi, c in self._edges) + 1
            )
            dummy = g.add_edge(rank[self._s], rank[self._t], limit, dummy_cost)
        sent, _ = g.flow(demand)
        if sent != demand:
            return -1, 0
        self._edge_flow = [
            e[2] + g.get_edge(i).flow for i, e in enumerate(self._edges)
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
