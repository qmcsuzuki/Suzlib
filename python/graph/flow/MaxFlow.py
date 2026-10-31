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
        """残余グラフで s から t に流し、今回追加した流量を返す。

        呼び出しごとに始点・終点を変更できる。返り値を d とすると、
        流出量 - 流入量は s で d 増え、t で d 減り、他では変わらない。
        現在の s-t 流量が F なら flow(t, s, D) (0 <= D <= F) は
        D を返し、総流量を F-D にする。flow(a, s, D) は、返り値の分だけ
        供給元を s から a に移す。異なる端点での呼び出し後は、元の
        s-t フローの流量保存則を満たすとは限らない。
        flow_limit=None は制限なし。一般に O(V^2 E) 時間、O(V) 追加空間。
        """
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

    def increase_edge(self, i: int, limit: int | None = None) -> int:
        """全頂点の収支を保ち、辺 i の流量を増やし、実際の増加量を返す。

        limit は非負の増加量上限。None なら可能な限り増やす。
        現在のフローも更新する。最大流である必要はなく、最大流に適用すれば
        総流量と最大性を保つ。他の辺の流量は固定しない。
        自己ループは直接更新し、それ以外は最大流を高々1回呼ぶ。
        一般に O(V^2 E) 時間、O(V) 追加空間。

        使用例:
            F = g.flow(s, t)
            d = g.increase_edge(i)  # 総流量 F を保って指定辺を最大化
            maximum = g.get_edge(i).flow
        """
        assert 0 <= i < (len(self._to) >> 1)
        j = i << 1
        cap = self._cap
        forward, reverse = cap[j], cap[j ^ 1]
        if limit is None:
            limit = forward
        else:
            assert limit >= 0
            limit = min(limit, forward)
        if limit == 0:
            return 0
        u, v = self._to[j ^ 1], self._to[j]
        if u == v:
            delta = limit
        else:
            # 指定辺の取り消しを禁止。正方向 u→v は v-u 増加路に入らない。
            cap[j ^ 1] = 0
            delta = self.flow(v, u, limit)
        cap[j] = forward - delta
        cap[j ^ 1] = reverse + delta
        return delta

    def decrease_edge(self, i: int, limit: int | None = None) -> int:
        """全頂点の収支を保ち、辺 i の流量を減らし、実際の減少量を返す。

        limit は非負の減少量上限。None なら可能な限り減らす。
        現在のフローも更新する。最大流である必要はなく、最大流に適用すれば
        総流量と最大性を保つ。他の辺の流量は固定しない。
        limit に届かなくても、迂回できた分の変更は反映される。
        自己ループは直接更新し、それ以外は最大流を高々1回呼ぶ。
        一般に O(V^2 E) 時間、O(V) 追加空間。

        使用例:
            e = g.get_edge(i)
            required = max(0, e.flow - new_cap)  # new_cap >= 0
            moved = g.decrease_edge(i, required)
            if moved == required:
                g.change_edge(i, new_cap, e.flow - moved)
            # 未達なら容量は元のまま。迂回後も元の収支を満たす。
        """
        assert 0 <= i < (len(self._to) >> 1)
        j = i << 1
        cap = self._cap
        forward, reverse = cap[j], cap[j ^ 1]
        if limit is None:
            limit = reverse
        else:
            assert limit >= 0
            limit = min(limit, reverse)
        if limit == 0:
            return 0
        u, v = self._to[j ^ 1], self._to[j]
        if u == v:
            delta = limit
        else:
            # 指定辺への再送を禁止。逆方向 v→u は u-v 増加路に入らない。
            cap[j] = 0
            delta = self.flow(u, v, limit)
        cap[j] = forward + delta
        cap[j ^ 1] = reverse - delta
        return delta

    def change_capacity(self, i: int, new_cap: int, s: int, t: int) -> int:
        """最大 s-t フローを保つよう辺 i の容量を変更し、総流量の変化量を返す。
        change_edge とは異なり、呼び出し前も後も最大流が流れていることが不変条件
        使用例:
            F = g.flow(s, t)
            F += g.change_capacity(i, new_cap, s, t)
            F += g.change_capacity(i, 0, s, t)  # 辺を無効化
        注意: 無向辺を2本の有向辺で表した場合は両方を更新する必要がある
        """
        assert 0 <= i < (len(self._to) >> 1)
        assert 0 <= s < self._n and 0 <= t < self._n and s != t
        assert new_cap >= 0
        e = self.get_edge(i)
        if new_cap >= e.flow:
            self.change_edge(i, new_cap, e.flow)
            if new_cap > e.cap:
                return self.flow(s, t, new_cap - e.cap)
            return 0

        required = e.flow - new_cap
        moved = self.decrease_edge(i, required)
        lost = required - moved
        self.change_edge(i, new_cap, new_cap)
        if lost:
            # 迂回を流し切ったので、残る指定辺の流れは循環には含まれない。
            # 指定辺の流量を lost 減らして生じた収支のずれを解消する。
            if e.src != s:
                canceled = self.flow(e.src, s, lost)
                assert canceled == lost
            if e.dst != t:
                canceled = self.flow(t, e.dst, lost)
                assert canceled == lost
        return -lost

    def min_cut(self, s: int) -> list[bool]:
        """各頂点 v について、残余グラフ上で s から v に到達可能なら True、
        到達不可能なら False となる長さ n のリストを返す。
        最大流が流れている状態なら、これは min cut の一つである。
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
