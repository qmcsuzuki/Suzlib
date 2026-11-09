# competitive-verifier: TITLE 最小費用流（最短路反復法、primal-dual）
# Ported from not522/ac-library-python:
# https://github.com/not522/ac-library-python/blob/master/atcoder/mincostflow.py
# Original repository license: CC0-1.0
# https://github.com/not522/ac-library-python/blob/master/LICENSE

from heapq import heappop, heappush
from typing import NamedTuple


class MCFGraph:
    """ポテンシャル付き最短路法による最小費用流。辺コストは非負を仮定する。
    flow / slope / min_cost_flow の呼び出しは、合わせて一度だけ可能。
    """

    class Edge(NamedTuple):
        """最小費用流グラフの辺の始点・終点・容量・流量・コストを保持する。"""
        src: int
        dst: int
        cap: int
        flow: int
        cost: int

    class _Edge:
        def __init__(self, dst: int, cap: int, cost: int) -> None:
            self.dst = dst
            self.cap = cap
            self.cost = cost
            self.rev: MCFGraph._Edge

    def __init__(self, n: int, dense: bool = False) -> None:
        """n 頂点の辺のないグラフを初期化する。
        dense = True だと O(N^2) の Dijkstra に内部アルゴリズムを変更
        """
        self._n = n
        self._dense = dense
        self._g: list[list[MCFGraph._Edge]] = [[] for _ in range(n)]
        self._edges: list[MCFGraph._Edge] = []
        self._used = False

    def add_edge(self, src: int, dst: int, cap: int, cost: int) -> int:
        """src から dst への容量 cap、単位費用 cost の辺を追加し、辺番号を返す。"""
        assert 0 <= src < self._n
        assert 0 <= dst < self._n
        assert 0 <= cap
        assert 0 <= cost
        m = len(self._edges)
        e = MCFGraph._Edge(dst, cap, cost)
        re = MCFGraph._Edge(src, 0, -cost)
        e.rev = re
        re.rev = e
        self._g[src].append(e)
        self._g[dst].append(re)
        self._edges.append(e)
        return m

    def get_edge(self, i: int) -> Edge:
        """i 番目に追加した辺の始点、終点、容量、現在の流量、コストを返す。"""
        assert 0 <= i < len(self._edges)
        e = self._edges[i]
        re = e.rev
        return MCFGraph.Edge(
            re.dst,
            e.dst,
            e.cap + re.cap,
            re.cap,
            e.cost,
        )

    def edges(self) -> list[Edge]:
        """追加した全ての辺を、追加順に返す。"""
        return [self.get_edge(i) for i in range(len(self._edges))]

    def flow(
        self,
        s: int,
        t: int,
        flow_limit: int | None = None,
    ) -> tuple[int, int]:
        """flow_limit 以下で流せる最大量まで流し、その (流量, 最小費用) を返す。"""
        return self.slope(s, t, flow_limit)[-1]

    def min_cost_flow(
        self,
        s: int,
        t: int,
        flow_limit: int | None = None,
    ) -> tuple[int, int]:
        """流量も選んで費用を最小化し、(総流量, 総費用) を返す。
        流量は 0 以上 flow_limit 以下（None は上限なし）。同費用なら流量最小。
        get_edge / edges で最適解の各辺の流量を取得できる。
        非負コストなので、このクラスでは常に (0, 0) となる。
        """
        return self._slope(s, t, flow_limit, 0)[-1]

    def slope(
        self,
        s: int,
        t: int,
        flow_limit: int | None = None,
    ) -> list[tuple[int, int]]:
        """各流量に対する最小費用の折れ線の頂点を返す。
        最後の点の流量は flow_limit 以下で流せる最大流量であり、そのフローを保持する。
        """
        return self._slope(s, t, flow_limit)

    def _slope(
        self,
        s: int,
        t: int,
        flow_limit: int | None,
        marginal_limit: int | None = None,
    ) -> list[tuple[int, int]]:
        # 限界費用が marginal_limit 以上なら、増流する前に停止する。
        assert not self._used
        n = self._n
        g = self._g
        assert 0 <= s < n
        assert 0 <= t < n
        assert s != t
        if flow_limit is None:
            flow_limit = sum(e.cap for e in g[s])
        else:
            assert 0 <= flow_limit
        self._used = True

        dual = [0] * n
        prev: list[MCFGraph._Edge | None] = [None] * n

        def refine_dual_sparse() -> bool:
            pq = []
            que_min = [s]
            visited = [False] * n
            dist = [-1] * n
            dist[s] = 0
            while que_min or pq:
                if que_min:
                    v = que_min.pop()
                    dist_v = dist[v]
                else:
                    dist_v, v = heappop(pq)
                if visited[v]:
                    continue
                visited[v] = True
                if v == t:
                    break
                dual_v = dual[v]
                for e in g[v]:
                    w = e.dst
                    if visited[w] or e.cap == 0:
                        continue
                    reduced_cost = e.cost - dual[w] + dual_v
                    new_dist = dist_v + reduced_cost
                    dist_w = dist[w]
                    if dist_w == -1 or new_dist < dist_w:
                        dist[w] = new_dist
                        prev[w] = e
                        if reduced_cost == 0:
                            que_min.append(w)
                        else:
                            heappush(pq, (new_dist, w))
            else:
                return False

            dist_t = dist[t]
            for v in range(n):
                if visited[v]:
                    dual[v] -= dist_t - dist[v]
            return True

        def refine_dual_dense() -> bool:
            visited = [False] * n
            dist = [-1] * n
            dist[s] = 0
            while True:
                v = -1
                for u in range(n):
                    if visited[u] or dist[u] == -1:
                        continue
                    if v == -1 or dist[u] < dist[v]:
                        v = u
                if v == -1:
                    return False
                visited[v] = True
                if v == t:
                    break
                dist_v = dist[v]
                dual_v = dual[v]
                for e in g[v]:
                    w = e.dst
                    if visited[w] or e.cap == 0:
                        continue
                    reduced_cost = e.cost - dual[w] + dual_v
                    new_dist = dist_v + reduced_cost
                    dist_w = dist[w]
                    if dist_w == -1 or new_dist < dist_w:
                        dist[w] = new_dist
                        prev[w] = e

            dist_t = dist[t]
            for v in range(n):
                if visited[v]:
                    dual[v] -= dist_t - dist[v]
            return True

        refine_dual = refine_dual_dense if self._dense else refine_dual_sparse

        flow = 0
        cost = 0
        prev_cost_per_flow: int | None = None
        result = [(flow, cost)]
        while flow < flow_limit:
            if not refine_dual():
                break

            c = -dual[s]
            if marginal_limit is not None and c >= marginal_limit:
                break

            f = flow_limit - flow
            v = t
            while v != s:
                e = prev[v]
                f = min(f, e.cap)
                v = e.rev.dst

            v = t
            while v != s:
                e = prev[v]
                re = e.rev
                e.cap -= f
                re.cap += f
                v = re.dst

            flow += f
            cost += f * c
            if c == prev_cost_per_flow:
                result.pop()
            result.append((flow, cost))
            prev_cost_per_flow = c

        return result


class DAGMCFGraph:
    """初期グラフが指定順の DAG のとき、負コスト辺を許す最小費用流。
    トポロジカル順は「s, s と t 以外の頂点を頂点番号順, t」。
    flow / slope / min_cost_flow の呼び出しは、合わせて一度だけ可能。
    """

    Edge = MCFGraph.Edge

    def __init__(self, n: int, s: int, t: int, dense: bool = False) -> None:
        """n 頂点、始点 s、終点 t のグラフを初期化する。
        dense=True では O(N^2) の密 Dijkstra を用いる。
        """
        assert 0 <= s < n
        assert 0 <= t < n
        assert s != t
        self._n = n
        self._s = s
        self._t = t
        self._dense = dense
        self._edges: list[tuple[int, int, int, int]] = []
        self._g: MCFGraph | None = None
        self._potential: list[int] | None = None
        self._used = False

    def _rank(self, v: int) -> int:
        if v == self._s:
            return -1
        if v == self._t:
            return self._n
        return v

    def add_edge(self, src: int, dst: int, cap: int, cost: int) -> int:
        """DAG の順方向へ容量 cap、単位費用 cost の辺を追加し、辺番号を返す。"""
        assert self._g is None
        assert 0 <= src < self._n
        assert 0 <= dst < self._n
        assert 0 <= cap
        assert self._rank(src) < self._rank(dst)
        self._edges.append((src, dst, cap, cost))
        return len(self._edges) - 1

    def get_edge(self, i: int) -> Edge:
        """i 番目に追加した辺を元のコストで返す。"""
        assert 0 <= i < len(self._edges)
        src, dst, cap, cost = self._edges[i]
        if self._g is None:
            return DAGMCFGraph.Edge(src, dst, cap, 0, cost)
        e = self._g.get_edge(i)
        return DAGMCFGraph.Edge(e.src, e.dst, e.cap, e.flow, cost)

    def edges(self) -> list[Edge]:
        """追加した全ての辺を、元のコストで追加順に返す。"""
        return [self.get_edge(i) for i in range(len(self._edges))]

    def _build(self) -> None:
        if self._g is not None:
            return

        adj: list[list[tuple[int, int]]] = [[] for _ in range(self._n)]
        for src, dst, _, cost in self._edges:
            adj[src].append((dst, cost))

        # 仮想 source から全頂点へ費用 0 の辺を張った最短距離。
        potential = [0] * self._n
        order = [self._s]
        order.extend(v for v in range(self._n) if v != self._s and v != self._t)
        order.append(self._t)
        for src in order:
            p = potential[src]
            for dst, cost in adj[src]:
                nd = p + cost
                if nd < potential[dst]:
                    potential[dst] = nd

        graph = MCFGraph(self._n, dense=self._dense)
        for src, dst, cap, cost in self._edges:
            reduced_cost = cost + potential[src] - potential[dst]
            assert 0 <= reduced_cost
            graph.add_edge(src, dst, cap, reduced_cost)

        self._g = graph
        self._potential = potential

    def flow(self, flow_limit: int | None = None) -> tuple[int, int]:
        """flow_limit 以下で流せる最大量まで流し、その (流量, 最小費用) を元のコストで返す。"""
        return self.slope(flow_limit)[-1]

    def min_cost_flow(self, flow_limit: int | None = None) -> tuple[int, int]:
        """流量も選んで費用を最小化し、元のコストで (総流量, 総費用) を返す。
        流量は 0 以上 flow_limit 以下（None は上限なし）。同費用なら流量最小。
        get_edge / edges で最適解の各辺の流量を取得できる。
        """
        return self._slope(flow_limit, True)[-1]

    def slope(
        self,
        flow_limit: int | None = None,
    ) -> list[tuple[int, int]]:
        """各流量に対する最小費用の折れ線の頂点を、元のコストで返す。
        最後の点に対応する最大流量のフローを保持する。
        """
        return self._slope(flow_limit)

    def _slope(
        self,
        flow_limit: int | None,
        minimize_cost: bool = False,
    ) -> list[tuple[int, int]]:
        assert not self._used
        self._build()
        self._used = True

        graph = self._g
        potential = self._potential
        assert graph is not None
        assert potential is not None
        shift = potential[self._s] - potential[self._t]
        # 元の限界費用は変換後の限界費用 - shift。
        result = graph._slope(
            self._s, self._t, flow_limit, shift if minimize_cost else None
        )
        return [(flow, cost - flow * shift) for flow, cost in result]
