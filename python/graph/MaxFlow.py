# competitive-verifier: TITLE Dinic法（最大流）
# Ported from not522/ac-library-python:
# https://github.com/not522/ac-library-python/blob/master/atcoder/maxflow.py
# Original repository license: CC0-1.0
# https://github.com/not522/ac-library-python/blob/master/LICENSE
# Residual edge indexing adapted from navel-tos/cp-library-for-codon:
# https://github.com/navel-tos/cp-library-for-codon/blob/main/algorithm/maxflow/maxflow.py
# Original repository license: CC0-1.0
# https://github.com/navel-tos/cp-library-for-codon/blob/main/LICENSE

from typing import NamedTuple


class MFGraph:
    """Dinic法による最大流。計算量は一般に O(V^2 E)。"""

    class Edge(NamedTuple):
        src: int
        dst: int
        cap: int
        flow: int

    def __init__(self, n: int) -> None:
        assert 0 <= n
        self._n = n
        self._g: list[list[int]] = [[] for _ in range(n)]
        self._to: list[int] = []
        self._cap: list[int] = []

    def add_edge(self, src: int, dst: int, cap: int) -> int:
        """src から dst への容量 cap の辺を追加し、辺番号を返す。"""
        assert 0 <= src < self._n
        assert 0 <= dst < self._n
        assert 0 <= cap
        edge_id = len(self._to) >> 1
        i = len(self._to)
        self._g[src].append(i)
        self._to.append(dst)
        self._cap.append(cap)
        self._g[dst].append(i ^ 1)
        self._to.append(src)
        self._cap.append(0)
        return edge_id

    def get_edge(self, i: int) -> Edge:
        """i 番目に追加した辺の始点、終点、容量、現在の流量を返す。"""
        assert 0 <= i < (len(self._to) >> 1)
        i <<= 1
        return MFGraph.Edge(
            self._to[i ^ 1],
            self._to[i],
            self._cap[i] + self._cap[i ^ 1],
            self._cap[i ^ 1],
        )

    def edges(self) -> list[Edge]:
        """追加した全ての辺を、追加順に返す。"""
        return [self.get_edge(i) for i in range(len(self._to) >> 1)]

    def change_edge(self, i: int, new_cap: int, new_flow: int) -> None:
        """i 番目の辺の容量と流量を変更する。"""
        assert 0 <= i < (len(self._to) >> 1)
        assert 0 <= new_flow <= new_cap
        i <<= 1
        self._cap[i] = new_cap - new_flow
        self._cap[i ^ 1] = new_flow

    def flow(self, s: int, t: int, flow_limit: int | None = None) -> int:
        """s から t へ追加で流せる流量を返す。"""
        n = self._n
        assert 0 <= s < n
        assert 0 <= t < n
        assert s != t

        g = self._g
        to = self._to
        cap = self._cap
        if flow_limit is None:
            flow_limit = sum(cap[i] for i in g[s])
        else:
            assert 0 <= flow_limit

        current_edge = [0] * n
        level = [n] * n

        def bfs() -> bool:
            for v in range(n):
                level[v] = n
            level[s] = 0
            queue = [s]
            q_front = 0
            while q_front < len(queue):
                v = queue[q_front]
                q_front += 1
                next_level = level[v] + 1
                for i in g[v]:
                    u = to[i]
                    if cap[i] == 0 or level[u] != n:
                        continue
                    level[u] = next_level
                    if u == t:
                        return True
                    queue.append(u)
            return False

        # t からレベルグラフを逆向きにたどることで再帰を避ける。
        def dfs(limit: int) -> int:
            stack = [t]
            edge_stack: list[int] = []
            while stack:
                v = stack[-1]
                if v == s:
                    f = limit
                    for i in edge_stack:
                        if cap[i] < f:
                            f = cap[i]
                    for i in edge_stack:
                        cap[i] -= f
                        cap[i ^ 1] += f
                    return f

                prev_level = level[v] - 1
                while current_edge[v] < len(g[v]):
                    i = g[v][current_edge[v]]
                    reverse_i = i ^ 1
                    if level[to[i]] != prev_level or cap[reverse_i] == 0:
                        current_edge[v] += 1
                        continue
                    stack.append(to[i])
                    edge_stack.append(reverse_i)
                    break
                else:
                    stack.pop()
                    if edge_stack:
                        edge_stack.pop()
                    level[v] = n
            return 0

        result = 0
        while result < flow_limit:
            if not bfs():
                break
            for v in range(n):
                current_edge[v] = 0
            while result < flow_limit:
                f = dfs(flow_limit - result)
                if f == 0:
                    break
                result += f
        return result

    def min_cut(self, s: int) -> list[bool]:
        """残余グラフ上で s から到達可能な頂点を返す。"""
        assert 0 <= s < self._n
        visited = [False] * self._n
        visited[s] = True
        stack = [s]
        while stack:
            v = stack.pop()
            for i in self._g[v]:
                u = self._to[i]
                if self._cap[i] > 0 and not visited[u]:
                    visited[u] = True
                    stack.append(u)
        return visited
