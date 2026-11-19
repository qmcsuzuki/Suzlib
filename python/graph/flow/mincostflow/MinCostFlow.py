# competitive-verifier: TITLE 最小費用流（最短路反復法、primal-dual）
# Ported from not522/ac-library-python:
# https://github.com/not522/ac-library-python/blob/master/atcoder/mincostflow.py
# Original repository license: CC0-1.0
# https://github.com/not522/ac-library-python/blob/master/LICENSE

from heapq import heappop, heappush
from typing import NamedTuple


class MCFGraph:
    """ポテンシャル付き最短路法による最小費用流。
    正容量の負費用辺がある場合、正容量の辺全体が DAG であることを要する。
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
        self._has_negative_edge = False

    def add_edge(self, src: int, dst: int, cap: int, cost: int) -> int:
        """src から dst への容量 cap、単位費用 cost の辺を追加し、辺番号を返す。"""
        assert 0 <= src < self._n
        assert 0 <= dst < self._n
        assert 0 <= cap
        if cap > 0 and cost < 0:
            self._has_negative_edge = True
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
        return self._flow(s, t, flow_limit)

    def min_cost_flow(
        self,
        s: int,
        t: int,
        flow_limit: int | None = None,
    ) -> tuple[int, int]:
        """流量も選んで費用を最小化し、(総流量, 総費用) を返す。
        流量は 0 以上 flow_limit 以下（None は上限なし）。同費用なら流量最小。
        get_edge / edges で最適解の各辺の流量を取得できる。
        """
        return self._flow(s, t, flow_limit, minimize_cost=True)

    def slope(
        self,
        s: int,
        t: int,
        flow_limit: int | None = None,
    ) -> list[tuple[int, int]]:
        """各流量に対する最小費用の折れ線の頂点を返す。
        最後の点の流量は flow_limit 以下で流せる最大流量であり、そのフローを保持する。
        """
        points = [(0, 0)]
        self._flow(s, t, flow_limit, points=points)
        return points

    def _initial_dual(self, s: int, t: int) -> list[int]:
        # 仮想始点から全頂点への費用 0 の辺を含めた最短距離を求める。
        n = self._n
        dual = [0] * n
        processed = [False] * n
        order = [s]
        order.extend(v for v in range(n) if v != s and v != t)
        order.append(t)
        for u in order:
            processed[u] = True
            for e in self._g[u]:
                if e.cap == 0:
                    continue
                if processed[e.dst]:
                    return self._initial_dual_kahn()
                dual[e.dst] = min(dual[e.dst], dual[u] + e.cost)
        return dual

    def _initial_dual_kahn(self) -> list[int]:
        n = self._n
        dual = [0] * n
        indegree = [0] * n
        for e in self._edges:
            if e.cap > 0:
                indegree[e.dst] += 1
        order = [v for v in range(n) if indegree[v] == 0]
        for u in order:
            for e in self._g[u]:
                if e.cap == 0:
                    continue
                v = e.dst
                dual[v] = min(dual[v], dual[u] + e.cost)
                indegree[v] -= 1
                if indegree[v] == 0:
                    order.append(v)
        assert len(order) == n, "negative-cost edges require an initial DAG"
        return dual

    def _flow(
        self,
        s: int,
        t: int,
        flow_limit: int | None,
        *,
        minimize_cost: bool = False,
        points: list[tuple[int, int]] | None = None,
    ) -> tuple[int, int]:
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
        dual = self._initial_dual(s, t) if self._has_negative_edge else [0] * n
        self._used = True
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
        while flow < flow_limit:
            if not refine_dual():
                break

            # 更新後の最短路の各辺は reduced cost が 0。
            c = dual[t] - dual[s]
            if minimize_cost and c >= 0:
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
            if points is not None:
                if c == prev_cost_per_flow:
                    points.pop()
                points.append((flow, cost))
                prev_cost_per_flow = c

        return flow, cost
