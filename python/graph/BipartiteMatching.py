# competitive-verifier: TITLE 最大二部マッチング


class BipartiteMatching:
    """左右の頂点集合を明示した Hopcroft--Karp 法。計算量は O(E sqrt(V))。"""

    def __init__(self, n_left: int, n_right: int) -> None:
        assert 0 <= n_left
        assert 0 <= n_right
        self.n_left = n_left
        self.n_right = n_right
        self.g: list[list[int]] = [[] for _ in range(n_left)]
        self.mate_left = [-1] * n_left
        self.mate_right = [-1] * n_right
        self.size = 0
        self._solved = False

    def add_edge(self, left: int, right: int) -> None:
        """左頂点 left と右頂点 right を結ぶ辺を追加する。solve 後も追加できる。"""
        assert 0 <= left < self.n_left
        assert 0 <= right < self.n_right
        self.g[left].append(right)
        self._solved = False

    def solve(self) -> int:
        """現在のグラフの最大マッチング数を返す。"""
        if self._solved:
            return self.size

        n_left = self.n_left
        g = self.g
        mate_left = self.mate_left
        mate_right = self.mate_right
        inf = n_left + 1
        dist = [inf] * n_left
        current_edge = [0] * n_left

        def bfs() -> int:
            queue: list[int] = []
            for left in range(n_left):
                if mate_left[left] == -1:
                    dist[left] = 0
                    queue.append(left)
                else:
                    dist[left] = inf

            shortest = inf
            q_front = 0
            while q_front < len(queue):
                left = queue[q_front]
                q_front += 1
                next_dist = dist[left] + 1
                if next_dist > shortest:
                    continue
                for right in g[left]:
                    next_left = mate_right[right]
                    if next_left == -1:
                        shortest = next_dist
                    elif dist[next_left] == inf:
                        dist[next_left] = next_dist
                        queue.append(next_left)
            return shortest

        # 再帰を避け、左頂点と選んだ右頂点をスタックに積む。
        def dfs(start: int, shortest: int) -> bool:
            left = start
            left_stack: list[int] = []
            right_stack: list[int] = []
            while True:
                i = current_edge[left]
                adj = g[left]

                while i < len(adj):
                    right = adj[i]
                    i += 1
                    next_left = mate_right[right]

                    if next_left == -1:
                        if dist[left] + 1 != shortest:
                            continue
                        current_edge[left] = i
                        left_stack.append(left)
                        right_stack.append(right)
                        while left_stack:
                            u = left_stack.pop()
                            v = right_stack.pop()
                            mate_left[u] = v
                            mate_right[v] = u
                        return True

                    if dist[next_left] == dist[left] + 1:
                        current_edge[left] = i
                        left_stack.append(left)
                        right_stack.append(right)
                        left = next_left
                        break
                else:
                    current_edge[left] = i
                    dist[left] = inf
                    if not left_stack:
                        return False
                    left = left_stack.pop()
                    right_stack.pop()

        while True:
            shortest = bfs()
            if shortest == inf:
                break
            for left in range(n_left):
                current_edge[left] = 0
            for left in range(n_left):
                if mate_left[left] == -1 and dfs(left, shortest):
                    self.size += 1

        self._solved = True
        return self.size

    def matching_edges(self) -> list[tuple[int, int]]:
        """最大マッチングに使われる (左頂点, 右頂点) を返す。"""
        self.solve()
        return [
            (left, right)
            for left, right in enumerate(self.mate_left)
            if right != -1
        ]

    def mates(self) -> tuple[list[int], list[int]]:
        """左から右、右から左への対応をそれぞれ返す。未対応は -1。"""
        self.solve()
        return self.mate_left.copy(), self.mate_right.copy()

    def _reachable_sets(self) -> tuple[list[bool], list[bool]]:
        self.solve()
        seen_left = [False] * self.n_left
        seen_right = [False] * self.n_right
        queue: list[int] = []
        for left in range(self.n_left):
            if self.mate_left[left] == -1:
                seen_left[left] = True
                queue.append(left)

        q_front = 0
        while q_front < len(queue):
            left = queue[q_front]
            q_front += 1
            matched_right = self.mate_left[left]
            for right in self.g[left]:
                if right == matched_right or seen_right[right]:
                    continue
                seen_right[right] = True
                next_left = self.mate_right[right]
                if next_left != -1 and not seen_left[next_left]:
                    seen_left[next_left] = True
                    queue.append(next_left)
        return seen_left, seen_right

    def min_vertex_cover(self) -> tuple[list[int], list[int]]:
        """最小頂点被覆を (左頂点列, 右頂点列) で返す。"""
        seen_left, seen_right = self._reachable_sets()
        left = [v for v in range(self.n_left) if not seen_left[v]]
        right = [v for v in range(self.n_right) if seen_right[v]]
        return left, right

    def max_independent_set(self) -> tuple[list[int], list[int]]:
        """最大独立集合を (左頂点列, 右頂点列) で返す。"""
        seen_left, seen_right = self._reachable_sets()
        left = [v for v in range(self.n_left) if seen_left[v]]
        right = [v for v in range(self.n_right) if not seen_right[v]]
        return left, right


class GeneralBipartiteMatching:
    """頂点を一つの整数空間で与え、自動で二部彩色する最大二部マッチング。"""

    def __init__(self, n: int) -> None:
        assert 0 <= n
        self.n = n
        self.edges: list[tuple[int, int]] = []
        self.color = [-1] * n
        self.toL = [-1] * n
        self.toR = [-1] * n
        self.fromL: list[int] = []
        self.fromR: list[int] = []
        self.X2Y: list[list[int]] = []
        self.mateL: list[int] = []
        self.mateR: list[int] = []
        self.mate = [-1] * n
        self.size = 0
        self._matching: BipartiteMatching | None = None
        self._solved = False

    def add_edge(self, u: int, v: int) -> None:
        """頂点 u, v を結ぶ辺を追加する。solve 後は彩色を含めて再構築する。"""
        assert 0 <= u < self.n
        assert 0 <= v < self.n
        self.edges.append((u, v))
        self._solved = False

    def _bipartition(self) -> None:
        graph = [[] for _ in range(self.n)]
        for u, v in self.edges:
            graph[u].append(v)
            graph[v].append(u)

        color = [-1] * self.n
        for start in range(self.n):
            if color[start] != -1:
                continue
            color[start] = 0
            queue = [start]
            q_front = 0
            while q_front < len(queue):
                u = queue[q_front]
                q_front += 1
                next_color = color[u] ^ 1
                for v in graph[u]:
                    if color[v] == -1:
                        color[v] = next_color
                        queue.append(v)
                    elif color[v] != next_color:
                        raise ValueError("graph is not bipartite")
        self.color = color

    def _build_lr(self) -> None:
        self._bipartition()
        self.fromL = [v for v in range(self.n) if self.color[v] == 0]
        self.fromR = [v for v in range(self.n) if self.color[v] == 1]
        self.toL = [-1] * self.n
        self.toR = [-1] * self.n
        for left, v in enumerate(self.fromL):
            self.toL[v] = left
        for right, v in enumerate(self.fromR):
            self.toR[v] = right

        X2Y = [[] for _ in range(len(self.fromL))]
        for u, v in self.edges:
            if self.color[u] == 0:
                X2Y[self.toL[u]].append(self.toR[v])
            else:
                X2Y[self.toL[v]].append(self.toR[u])

        matching = BipartiteMatching(len(self.fromL), len(self.fromR))
        matching.g = X2Y
        self._matching = matching
        self.X2Y = X2Y

    def solve(self) -> int:
        """現在のグラフの最大マッチング数を返す。非二部グラフなら ValueError。"""
        if self._solved:
            return self.size
        self._build_lr()
        assert self._matching is not None
        self.size = self._matching.solve()
        self.mateL = self._matching.mate_left
        self.mateR = self._matching.mate_right
        self.mate = [-1] * self.n
        for left, right in enumerate(self.mateL):
            if right == -1:
                continue
            u = self.fromL[left]
            v = self.fromR[right]
            self.mate[u] = v
            self.mate[v] = u
        self._solved = True
        return self.size

    def matching_edges(self) -> list[tuple[int, int]]:
        """最大マッチングを (色0の頂点, 色1の頂点) の組で返す。"""
        self.solve()
        return [
            (self.fromL[left], self.fromR[right])
            for left, right in enumerate(self.mateL)
            if right != -1
        ]

    def mates(self) -> list[int]:
        """各頂点の対応先を返す。未対応は -1。"""
        self.solve()
        return self.mate.copy()

    def min_vertex_cover(self) -> list[int]:
        """元の頂点番号で最小頂点被覆を返す。"""
        self.solve()
        assert self._matching is not None
        left, right = self._matching.min_vertex_cover()
        return [self.fromL[v] for v in left] + [self.fromR[v] for v in right]

    def max_independent_set(self) -> list[int]:
        """元の頂点番号で最大独立集合を返す。"""
        self.solve()
        assert self._matching is not None
        left, right = self._matching.max_independent_set()
        return [self.fromL[v] for v in left] + [self.fromR[v] for v in right]
