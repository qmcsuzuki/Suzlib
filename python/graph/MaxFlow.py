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

    def residual_graph(self) -> list[list[int]]:
        """正の残余容量を持つ辺からなる隣接リストを返す。"""
        g = self._g
        to = self._to
        cap = self._cap
        return [[to[i] for i in g[v] if cap[i] > 0] for v in range(self._n)]

    def path_decomposition(self, s: int, t: int) -> list[tuple[int, list[int]]]:
        """現在の実行可能な s-t フローを (流量, 辺番号列) の和に分解する。

        閉路上の循環流は返さず、グラフの状態は変更しない。
        """
        n = self._n
        assert 0 <= s < n
        assert 0 <= t < n
        assert s != t

        to = self._to
        cap = self._cap
        m = len(to) >> 1
        remain = [0] * m
        graph = [[] for _ in range(n)]
        balance = [0] * n
        for edge_id in range(m):
            i = edge_id << 1
            f = cap[i ^ 1]
            remain[edge_id] = f
            if f == 0:
                continue
            src = to[i ^ 1]
            dst = to[i]
            graph[src].append(edge_id)
            balance[src] -= f
            balance[dst] += f

        for v in range(n):
            if v != s and v != t:
                assert balance[v] == 0
        assert balance[s] <= 0
        assert balance[t] == -balance[s]
        flow_value = -balance[s]

        current_edge = [0] * n
        position = [-1] * n
        result: list[tuple[int, list[int]]] = []
        decomposed = 0
        while decomposed < flow_value:
            vertices = [s]
            path: list[int] = []
            position[s] = 0

            while vertices[-1] != t:
                v = vertices[-1]
                while (
                    current_edge[v] < len(graph[v])
                    and remain[graph[v][current_edge[v]]] == 0
                ):
                    current_edge[v] += 1
                assert current_edge[v] < len(graph[v])

                edge_id = graph[v][current_edge[v]]
                u = to[edge_id << 1]
                path.append(edge_id)
                if position[u] == -1:
                    position[u] = len(vertices)
                    vertices.append(u)
                    continue

                # 閉路の流量を除いて単純なパスに戻す。
                cycle_start = position[u]
                cycle = path[cycle_start:]
                f = min(remain[edge_id] for edge_id in cycle)
                for edge_id in cycle:
                    remain[edge_id] -= f
                for x in vertices[cycle_start + 1 :]:
                    position[x] = -1
                del vertices[cycle_start + 1 :]
                del path[cycle_start:]

            f = min(remain[edge_id] for edge_id in path)
            if decomposed + f > flow_value:
                f = flow_value - decomposed
            for edge_id in path:
                remain[edge_id] -= f
            result.append((f, path.copy()))
            decomposed += f
            for v in vertices:
                position[v] = -1

        return result

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
