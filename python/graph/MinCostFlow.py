# competitive-verifier: TITLE 最小費用流
# Ported from not522/ac-library-python:
# https://github.com/not522/ac-library-python/blob/master/atcoder/mincostflow.py
# Original repository license: CC0-1.0
# https://github.com/not522/ac-library-python/blob/master/LICENSE

from heapq import heappop, heappush
from typing import List, NamedTuple, Optional, Tuple


class MCFGraph:
    """ポテンシャル付き最短路法による最小費用流。辺コストは非負を仮定する。"""

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

        dense=False では heap を用いる疎グラフ向け Dijkstra、dense=True では
        O(V^2 + E) の密グラフ向け Dijkstra を用いる。
        """
        self._n = n
        self._dense = dense
        self._g: List[List[MCFGraph._Edge]] = [[] for _ in range(n)]
        self._edges: List[MCFGraph._Edge] = []
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

    def edges(self) -> List[Edge]:
        """追加した全ての辺を、追加順に返す。"""
        return [self.get_edge(i) for i in range(len(self._edges))]

    def flow(
        self,
        s: int,
        t: int,
        flow_limit: Optional[int] = None,
    ) -> Tuple[int, int]:
        """s から t への最小費用流を (流量, 費用) で返す。"""
        return self.slope(s, t, flow_limit)[-1]

    def slope(
        self,
        s: int,
        t: int,
        flow_limit: Optional[int] = None,
    ) -> List[Tuple[int, int]]:
        """流量と最小費用の折れ線の頂点を返す。このメソッドは1回だけ呼べる。"""
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
        prev: List[Optional[MCFGraph._Edge]] = [None] * n

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
        prev_cost_per_flow: Optional[int] = None
        result = [(flow, cost)]
        while flow < flow_limit:
            if not refine_dual():
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

            c = -dual[s]
            flow += f
            cost += f * c
            if c == prev_cost_per_flow:
                result.pop()
            result.append((flow, cost))
            prev_cost_per_flow = c

        return result


class DAGMCFGraph:
    """初期グラフが指定順の DAG のとき、負コスト辺を許す最小費用流。

    トポロジカル順は
        s, s と t 以外の頂点を頂点番号順, t
    とする。最初に DAG DP でポテンシャルを求め、非負の reduced cost に
    変換した後は MCFGraph に処理を委ねる。
    """

    Edge = MCFGraph.Edge

    def __init__(self, n: int, s: int, t: int, dense: bool = False) -> None:
        """n 頂点、始点 s、終点 t のグラフを初期化する。

        dense=False では heap を用いる疎グラフ向け Dijkstra、dense=True では
        O(V^2 + E) の密グラフ向け Dijkstra を、初期ポテンシャル構築後の最短路計算に用いる。
        """
        assert 0 <= s < n
        assert 0 <= t < n
        assert s != t
        self._n = n
        self._s = s
        self._t = t
        self._dense = dense
        self._edges: List[Tuple[int, int, int, int]] = []
        self._g: Optional[MCFGraph] = None
        self._potential: Optional[List[int]] = None
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

    def edges(self) -> List[Edge]:
        """追加した全ての辺を、元のコストで追加順に返す。"""
        return [self.get_edge(i) for i in range(len(self._edges))]

    def _build(self) -> None:
        if self._g is not None:
            return

        adj: List[List[Tuple[int, int]]] = [[] for _ in range(self._n)]
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

    def flow(self, flow_limit: Optional[int] = None) -> Tuple[int, int]:
        """s から t への最小費用流を、元のコストで (流量, 費用) として返す。"""
        return self.slope(flow_limit)[-1]

    def slope(
        self,
        flow_limit: Optional[int] = None,
    ) -> List[Tuple[int, int]]:
        """流量と最小費用の折れ線の頂点を、元のコストで返す。"""
        assert not self._used
        self._build()
        self._used = True

        graph = self._g
        potential = self._potential
        assert graph is not None
        assert potential is not None
        result = graph.slope(self._s, self._t, flow_limit)
        shift = potential[self._s] - potential[self._t]
        return [(flow, cost - flow * shift) for flow, cost in result]
