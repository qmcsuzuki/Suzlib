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
        """最大流グラフの辺の始点・終点・容量・流量を保持する。"""
        src: int
        dst: int
        cap: int
        flow: int

    def __init__(self, n: int) -> None:
        """n 頂点の辺のない残余グラフを初期化する。"""
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
                f = min(map(remain.__getitem__, cycle))
                for e in cycle:
                    remain[e] -= f
                for x in vertices[cycle_start + 1 :]:
                    position[x] = -1
                del vertices[cycle_start + 1 :]
                del path[cycle_start:]

            f = min(remain[e] for e in path)
            if decomposed + f > flow_value:
                f = flow_value - decomposed
            for e in path:
                remain[e] -= f
            result.append((f, path))
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
        result = 0
        while result < flow_limit:
            # 残余グラフのレベルを BFS で設定する。
            for v in range(n):
                level[v] = n
            level[s] = 0
            queue = [s]
            q_front = 0
            reached = False
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
                        reached = True
                        break
                    queue.append(u)
                if reached:
                    break
            if not reached:
                break

            for v in range(n):
                current_edge[v] = 0

            # t からレベルグラフを逆向きにたどり、1 回の走査で
            # blocking flow を流す。増加後も使える suffix は保持する。
            stack = [t]
            edge_stack: list[int] = []
            while stack and result < flow_limit:
                v = stack[-1]
                if v == s:
                    f = flow_limit - result
                    for i in edge_stack:
                        if cap[i] < f:
                            f = cap[i]
                    for i in edge_stack:
                        cap[i] -= f
                        cap[i ^ 1] += f
                    result += f
                    if result == flow_limit:
                        break

                    # t に近い側から最初に飽和した辺まで巻き戻す。
                    k = 0
                    while cap[edge_stack[k]]:
                        k += 1
                    del stack[k + 1 :]
                    del edge_stack[k:]
                    continue

                prev_level = level[v] - 1
                gv = g[v]
                ce = current_edge[v]
                while ce < len(gv):
                    i = gv[ce]
                    reverse_i = i ^ 1
                    if level[to[i]] != prev_level or cap[reverse_i] == 0:
                        ce += 1
                        continue
                    current_edge[v] = ce
                    stack.append(to[i])
                    edge_stack.append(reverse_i)
                    break
                else:
                    current_edge[v] = ce
                    stack.pop()
                    if edge_stack:
                        edge_stack.pop()
                    level[v] = n
        return result

    def min_cut(self, s: int) -> list[bool]:
        """残余グラフ上で s から到達可能な頂点を返す。

        flow_limit による打ち切り後は、返す集合が最小カットとは限らない。
        """
        n = self._n
        assert 0 <= s < n
        g = self._g
        to = self._to
        cap = self._cap
        visited = [False] * n
        visited[s] = True
        stack = [s]
        while stack:
            v = stack.pop()
            for i in g[v]:
                u = to[i]
                if cap[i] > 0 and not visited[u]:
                    visited[u] = True
                    stack.append(u)
        return visited
