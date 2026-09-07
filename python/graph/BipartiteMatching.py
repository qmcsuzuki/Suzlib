# competitive-verifier: TITLE 最大二部マッチング

from random import shuffle


class BipartiteMatching:
    """Kuhn 法を前処理に用いた Hopcroft--Karp 法。計算量は O((V + E) sqrt(V))。"""

    def __init__(self, n_left: int, n_right: int) -> None:
        assert 0 <= n_left
        assert 0 <= n_right
        self.n_left = n_left
        self.n_right = n_right
        self.g: list[list[int]] = [[] for _ in range(n_left)]
        self.mate_left = [-1] * n_left
        self.mate_right = [-1] * n_right
        self.size = 0
        self._edge_shift = max(1, (n_right - 1).bit_length())
        self._edge_mask = (1 << self._edge_shift) - 1
        self._edges: list[int] = []
        self._removed_edges: set[int] = set()
        self._adj_built = False
        self._solved = False

    def add_edge(self, left: int, right: int) -> int:
        """左頂点 left と右頂点 right を結ぶ辺を追加し、辺番号を返す。solve 後も追加できる。"""
        assert 0 <= left < self.n_left
        assert 0 <= right < self.n_right
        edge_id = len(self._edges)
        self._edges.append((left << self._edge_shift) | right)
        if self._adj_built:
            self.g[left].append(right)
        self._solved = False
        return edge_id

    def edge_count(self) -> int:
        """これまでに発行した辺番号の個数を返す。削除済み辺も数える。"""
        return len(self._edges)

    def edges(self) -> list[tuple[int, int, int]]:
        """現在存在する辺を (edge_id, left, right) で返す。"""
        shift = self._edge_shift
        mask = self._edge_mask
        removed = self._removed_edges
        return [
            (edge_id, edge >> shift, edge & mask)
            for edge_id, edge in enumerate(self._edges)
            if edge_id not in removed
        ]

    def _build_adjacency(self) -> None:
        """初回 solve 時に packed edge を sort し、左頂点ごとの隣接リストを構築する。"""
        if self._adj_built:
            return
        edges = sorted(self._edges)
        shift = self._edge_shift
        mask = self._edge_mask
        start = [0] * (self.n_left + 1)
        i = 0
        m = len(edges)
        for left in range(self.n_left):
            threshold = (left + 1) << shift
            while i < m and edges[i] < threshold:
                i += 1
            start[left + 1] = i
        self.g = [
            [edge & mask for edge in edges[start[left]:start[left + 1]]]
            for left in range(self.n_left)
        ]
        self._adj_built = True

    def _degree_greedy(self) -> int:
        """低次数頂点を優先して初期マッチングを構成する。"""
        g = self.g
        mate_left = self.mate_left
        mate_right = self.mate_right
        n_left = self.n_left
        n_right = self.n_right

        reverse = [[] for _ in range(n_right)]
        degree_left = [len(adj) for adj in g]
        degree_right = [0] * n_right
        for left, adj in enumerate(g):
            for right in adj:
                reverse[right].append(left)
                degree_right[right] += 1

        leaves = [left for left in range(n_left) if degree_left[left] == 1]
        leaves += [n_left + right for right in range(n_right) if degree_right[right] == 1]
        twos = [left for left in range(n_left) if degree_left[left] == 2]
        twos += [n_left + right for right in range(n_right) if degree_right[right] == 2]

        added = 0
        scan = 0
        while True:
            while leaves:
                v = leaves[-1]
                degree = degree_left[v] if v < n_left else degree_right[v - n_left]
                if degree == 1:
                    break
                leaves.pop()

            if leaves:
                v = leaves.pop()
                if v < n_left:
                    left = v
                    right = -1
                    for w in g[left]:
                        if degree_right[w]:
                            right = w
                            break
                else:
                    right = v - n_left
                    left = -1
                    for w in reverse[right]:
                        if degree_left[w]:
                            left = w
                            break
            else:
                while scan < n_left and degree_left[scan] == 0:
                    scan += 1
                if scan == n_left:
                    break

                while twos:
                    v = twos[-1]
                    degree = degree_left[v] if v < n_left else degree_right[v - n_left]
                    if degree == 2:
                        break
                    twos.pop()
                v = twos.pop() if twos else scan

                if v < n_left:
                    left = v
                    right = -1
                    best = len(self._edges) + 1
                    for w in g[left]:
                        degree = degree_right[w]
                        if 0 < degree < best:
                            right = w
                            best = degree
                else:
                    right = v - n_left
                    left = -1
                    best = len(self._edges) + 1
                    for w in reverse[right]:
                        degree = degree_left[w]
                        if 0 < degree < best:
                            left = w
                            best = degree

            if left == -1 or right == -1:
                continue

            mate_left[left] = right
            mate_right[right] = left
            added += 1
            degree_left[left] = 0
            degree_right[right] = 0

            for w in g[left]:
                if degree_right[w]:
                    degree_right[w] -= 1
                    if degree_right[w] == 1:
                        leaves.append(n_left + w)
                    elif degree_right[w] == 2:
                        twos.append(n_left + w)
            for w in reverse[right]:
                if degree_left[w]:
                    degree_left[w] -= 1
                    if degree_left[w] == 1:
                        leaves.append(w)
                    elif degree_left[w] == 2:
                        twos.append(w)

        return added

    def solve(self) -> int:
        """現在のグラフの最大マッチング数を返す。"""
        if self._solved:
            return self.size

        self._build_adjacency()
        g = self.g
        mate_left = self.mate_left
        mate_right = self.mate_right

        # Kuhn 法が入力順に依存しすぎないよう、各左頂点の隣接順をランダム化する。
        for adj in g:
            if len(adj) > 1:
                shuffle(adj)

        if self.size == 0:
            self.size = self._degree_greedy()

            if self.size == 0:
                self._solved = True
                return 0
            if self.size == min(self.n_left, self.n_right):
                self._solved = True
                return self.size

        def kuhn_phase() -> int:
            """全未マッチ左頂点から交互森を伸ばし、増大路を貪欲に反転する。"""
            parent = [-1] * self.n_left
            root = [-1] * self.n_left
            queue: list[int] = []

            for left in range(self.n_left):
                if mate_left[left] == -1:
                    parent[left] = -2
                    root[left] = left
                    queue.append(left)

            added = 0
            q_front = 0
            while q_front < len(queue):
                left = queue[q_front]
                q_front += 1

                # この根から既に増大したなら、残りの交互木は探索しない。
                if mate_left[root[left]] != -1:
                    continue

                matched_right = mate_left[left]
                for right in g[left]:
                    if right == matched_right:
                        continue
                    next_left = mate_right[right]

                    if next_left == -1:
                        while left >= 0:
                            mate_right[right] = left
                            right, mate_left[left] = mate_left[left], right
                            left = parent[left]
                        added += 1
                        break

                    if parent[next_left] == -1:
                        parent[next_left] = left
                        root[next_left] = root[left]
                        queue.append(next_left)

            return added

        # Kuhn 型の交互森を先に最大 128 phase 回す。
        for _ in range(128):
            added = kuhn_phase()
            self.size += added
            if added == 0 or self.size == min(self.n_left, self.n_right):
                self._solved = True
                return self.size

        inf = self.n_left + 1
        dist = [inf] * self.n_left
        current_edge: list[int] = []

        def bfs() -> int:
            """未マッチ左頂点から BFS し、最短増大路の長さを返す。"""
            queue: list[int] = []
            for left in range(self.n_left):
                if mate_left[left] == -1:
                    dist[left] = 0
                    queue.append(left)
                else:
                    dist[left] = inf

            q_front = 0
            while q_front < len(queue):
                left = queue[q_front]
                q_front += 1
                next_dist = dist[left] + 1
                for right in g[left]:
                    next_left = mate_right[right]
                    if next_left == -1:
                        return next_dist
                    if dist[next_left] == inf:
                        dist[next_left] = next_dist
                        queue.append(next_left)
            return inf

        # 再帰を避け、左頂点をスタックに積む。
        def dfs(start: int, shortest: int) -> bool:
            """BFS 層に沿って最短増大路を1本探し、見つかれば反転する。"""
            left = start
            left_stack: list[int] = []
            while True:
                i = current_edge[left]
                adj = g[left]
                n_adj = len(adj)
                target = dist[left] + 1

                while i < n_adj:
                    right = adj[i]
                    i += 1
                    next_left = mate_right[right]

                    if next_left == -1:
                        if target != shortest:
                            continue
                        current_edge[left] = i
                        while True:
                            mate_right[right] = left
                            right, mate_left[left] = mate_left[left], right
                            if right == -1:
                                return True
                            left = left_stack.pop()

                    if dist[next_left] == target:
                        current_edge[left] = i
                        left_stack.append(left)
                        left = next_left
                        break
                else:
                    current_edge[left] = i
                    dist[left] = inf
                    if not left_stack:
                        return False
                    left = left_stack.pop()

        while True:
            shortest = bfs()
            if shortest == inf:
                break
            current_edge = [0] * self.n_left
            for left in range(self.n_left):
                if mate_left[left] == -1 and dfs(left, shortest):
                    self.size += 1

        self._solved = True
        return self.size

    def _augment_once(self) -> bool:
        """全ての未マッチ左頂点から交互 BFS を1回だけ行い、増大路を1本だけ反転する。"""
        g = self.g
        mate_left = self.mate_left
        mate_right = self.mate_right

        queue: list[int] = []
        parent = [-1] * self.n_left
        seen = [False] * self.n_left
        for left in range(self.n_left):
            if mate_left[left] == -1:
                seen[left] = True
                queue.append(left)

        q_front = 0
        while q_front < len(queue):
            left = queue[q_front]
            q_front += 1
            matched_right = mate_left[left]
            for right in g[left]:
                if right == matched_right:
                    continue
                next_left = mate_right[right]
                if next_left == -1:
                    while right != -1:
                        mate_right[right] = left
                        right, mate_left[left] = mate_left[left], right
                        left = parent[left]
                    self.size += 1
                    return True
                if not seen[next_left]:
                    seen[next_left] = True
                    parent[next_left] = left
                    queue.append(next_left)
        return False

    def increment_edge(self, left: int, right: int) -> bool:
        """最大マッチング構築後に辺を1本追加し、サイズが増えたかを返す。"""
        if not self._solved:
            raise RuntimeError("call solve() before increment_edge()")
        assert 0 <= left < self.n_left
        assert 0 <= right < self.n_right
        self._edges.append((left << self._edge_shift) | right)
        self.g[left].append(right)

        if self.size == min(self.n_left, self.n_right):
            return False
        if self.mate_left[left] == -1 and self.mate_right[right] == -1:
            self.mate_left[left] = right
            self.mate_right[right] = left
            self.size += 1
            return True
        return self._augment_once()

    def increment_edges_from_left(self, left: int, rights: list[int]) -> bool:
        """最大マッチング構築後に一つの左頂点から複数辺を追加し、サイズが増えたかを返す。"""
        if not self._solved:
            raise RuntimeError("call solve() before increment_edges_from_left()")
        assert 0 <= left < self.n_left
        for right in rights:
            assert 0 <= right < self.n_right
        base = left << self._edge_shift
        self._edges.extend(base | right for right in rights)
        self.g[left].extend(rights)

        if self.size == min(self.n_left, self.n_right):
            return False
        if self.mate_left[left] == -1:
            for right in rights:
                if self.mate_right[right] == -1:
                    self.mate_left[left] = right
                    self.mate_right[right] = left
                    self.size += 1
                    return True
        return self._augment_once()

    def increment_edges_from_right(self, right: int, lefts: list[int]) -> bool:
        """最大マッチング構築後に一つの右頂点へ複数辺を追加し、サイズが増えたかを返す。"""
        if not self._solved:
            raise RuntimeError("call solve() before increment_edges_from_right()")
        assert 0 <= right < self.n_right
        for left in lefts:
            assert 0 <= left < self.n_left
            self._edges.append((left << self._edge_shift) | right)
            self.g[left].append(right)

        if self.size == min(self.n_left, self.n_right):
            return False
        if self.mate_right[right] == -1:
            for left in lefts:
                if self.mate_left[left] == -1:
                    self.mate_left[left] = right
                    self.mate_right[right] = left
                    self.size += 1
                    return True
        return self._augment_once()

    def remove_edge(self, edge_id: int) -> bool:
        """最大マッチング構築後に辺番号 edge_id の辺を削除し、最大マッチング数が減ったかを返す。"""
        if not self._solved:
            raise RuntimeError("call solve() before remove_edge()")
        assert 0 <= edge_id < len(self._edges)
        if edge_id in self._removed_edges:
            raise ValueError("edge is already removed")

        edge = self._edges[edge_id]
        left = edge >> self._edge_shift
        right = edge & self._edge_mask
        self._removed_edges.add(edge_id)
        self.g[left].remove(right)

        if self.mate_left[left] != right:
            return False

        self.mate_left[left] = -1
        self.mate_right[right] = -1
        self.size -= 1
        return not self._augment_once()

    def matching_edges(self) -> list[tuple[int, int]]:
        """最大マッチングに使われる (左頂点, 右頂点) を返す。"""
        self.solve()
        return [
            (left, right)
            for left, right in enumerate(self.mate_left)
            if right != -1
        ]

    def matching_edge_ids(self) -> list[int]:
        """最大マッチングに対応する入力辺番号を返す。多重辺では最初の辺を選ぶ。"""
        self.solve()
        edge_for_left = [-1] * self.n_left
        shift = self._edge_shift
        mask = self._edge_mask
        removed = self._removed_edges
        for edge_id, edge in enumerate(self._edges):
            if edge_id in removed:
                continue
            left = edge >> shift
            if edge_for_left[left] != -1:
                continue
            right = edge & mask
            if self.mate_left[left] == right:
                edge_for_left[left] = edge_id
        return [edge_id for edge_id in edge_for_left if edge_id != -1]

    def mates(self) -> tuple[list[int], list[int]]:
        """左から右、右から左への対応をそれぞれ返す。未対応は -1。"""
        self.solve()
        return self.mate_left.copy(), self.mate_right.copy()

    def _reachable_sets(self) -> tuple[list[bool], list[bool]]:
        """未マッチ左頂点から交互路で到達可能な左右の頂点集合を返す。"""
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

    def add_edge(self, u: int, v: int) -> int:
        """頂点 u, v を結ぶ辺を追加し、辺番号を返す。solve 後は彩色を含めて再構築する。"""
        assert 0 <= u < self.n
        assert 0 <= v < self.n
        edge_id = len(self.edges)
        self.edges.append((u, v))
        self._solved = False
        return edge_id

    def _bipartition(self) -> None:
        """現在の辺集合を二部彩色し、各頂点の色を self.color に保存する。"""
        graph = [[] for _ in range(self.n)]
        for u, v in self.edges:
            graph[u].append(v)
            graph[v].append(u)

        color = [-1] * self.n
        for start in range(self.n):
            if color[start] != -1:
                continue
            color[start] = 1
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
        """二部彩色を左右に圧縮し、内部の BipartiteMatching を構築する。"""
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
        matching = BipartiteMatching(len(self.fromL), len(self.fromR))
        packed_edges: list[int] = []
        shift = matching._edge_shift
        for u, v in self.edges:
            if self.color[u] == 0:
                left = self.toL[u]
                right = self.toR[v]
            else:
                left = self.toL[v]
                right = self.toR[u]
            X2Y[left].append(right)
            packed_edges.append((left << shift) | right)

        matching.g = X2Y
        matching._edges = packed_edges
        matching._adj_built = True
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

    def matching_edge_ids(self) -> list[int]:
        """最大マッチングに対応する入力辺番号を返す。多重辺では最初の辺を選ぶ。"""
        self.solve()
        assert self._matching is not None
        return self._matching.matching_edge_ids()

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