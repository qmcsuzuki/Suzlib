# competitive-verifier: TITLE 最大二部マッチング CSR 実験

from random import shuffle


class BipartiteMatchingCSR:
    """CSR で隣接辺を保持する最大二部マッチングの速度実験用実装。"""

    def __init__(self, n_left: int, n_right: int) -> None:
        assert 0 <= n_left
        assert 0 <= n_right
        self.n_left = n_left
        self.n_right = n_right
        self.mate_left = [-1] * n_left
        self.mate_right = [-1] * n_right
        self.size = 0
        self._edge_shift = max(1, (n_right - 1).bit_length())
        self._edge_mask = (1 << self._edge_shift) - 1
        self._edges: list[int] = []
        self._start: list[int] = []
        self._to: list[int] = []
        self._solved = False

    def add_edge(self, left: int, right: int) -> int:
        assert 0 <= left < self.n_left
        assert 0 <= right < self.n_right
        edge_id = len(self._edges)
        self._edges.append((left << self._edge_shift) | right)
        self._solved = False
        return edge_id

    def _build_csr(self) -> None:
        """辺を左頂点ごとの CSR に $O(V+E)$ でまとめ、隣接順をランダム化する。"""
        edges = self._edges.copy()
        shuffle(edges)
        shift = self._edge_shift
        mask = self._edge_mask

        start = [0] * (self.n_left + 1)
        for edge in edges:
            start[(edge >> shift) + 1] += 1
        for left in range(self.n_left):
            start[left + 1] += start[left]

        to = [0] * len(edges)
        pos = start[:-1].copy()
        for edge in edges:
            left = edge >> shift
            to[pos[left]] = edge & mask
            pos[left] += 1

        self._start = start
        self._to = to

    def _degree_greedy(self) -> int:
        """左右両側の CSR を用いて低次数頂点を優先した初期マッチングを作る。"""
        start = self._start
        to = self._to
        mate_left = self.mate_left
        mate_right = self.mate_right
        n_left = self.n_left
        n_right = self.n_right

        rstart = [0] * (n_right + 1)
        for right in to:
            rstart[right + 1] += 1
        for right in range(n_right):
            rstart[right + 1] += rstart[right]

        rto = [0] * len(to)
        pos = rstart[:-1].copy()
        for left in range(n_left):
            for i in range(start[left], start[left + 1]):
                right = to[i]
                rto[pos[right]] = left
                pos[right] += 1

        degree_left = [start[left + 1] - start[left] for left in range(n_left)]
        degree_right = [rstart[right + 1] - rstart[right] for right in range(n_right)]

        leaves = [left for left in range(n_left) if degree_left[left] == 1]
        leaves += [n_left + right for right in range(n_right) if degree_right[right] == 1]
        twos = [left for left in range(n_left) if degree_left[left] == 2]
        twos += [n_left + right for right in range(n_right) if degree_right[right] == 2]

        added = 0
        scan = 0
        m = len(to)
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
                    for i in range(start[left], start[left + 1]):
                        w = to[i]
                        if degree_right[w]:
                            right = w
                            break
                else:
                    right = v - n_left
                    left = -1
                    for i in range(rstart[right], rstart[right + 1]):
                        w = rto[i]
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
                    best = m + 1
                    for i in range(start[left], start[left + 1]):
                        w = to[i]
                        degree = degree_right[w]
                        if 0 < degree < best:
                            right = w
                            best = degree
                else:
                    right = v - n_left
                    left = -1
                    best = m + 1
                    for i in range(rstart[right], rstart[right + 1]):
                        w = rto[i]
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

            for i in range(start[left], start[left + 1]):
                w = to[i]
                if degree_right[w]:
                    degree_right[w] -= 1
                    if degree_right[w] == 1:
                        leaves.append(n_left + w)
                    elif degree_right[w] == 2:
                        twos.append(n_left + w)
            for i in range(rstart[right], rstart[right + 1]):
                w = rto[i]
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

        self._build_csr()
        start = self._start
        to = self._to
        mate_left = self.mate_left
        mate_right = self.mate_right

        if self.size == 0:
            self.size = self._degree_greedy()

            if self.size == 0:
                self._solved = True
                return 0
            if self.size == min(self.n_left, self.n_right):
                self._solved = True
                return self.size

        def kuhn_phase() -> int:
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

                if mate_left[root[left]] != -1:
                    continue

                matched_right = mate_left[left]
                for i in range(start[left], start[left + 1]):
                    right = to[i]
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
                for i in range(start[left], start[left + 1]):
                    right = to[i]
                    next_left = mate_right[right]
                    if next_left == -1:
                        return next_dist
                    if dist[next_left] == inf:
                        dist[next_left] = next_dist
                        queue.append(next_left)
            return inf

        def dfs(start_left: int, shortest: int) -> bool:
            left = start_left
            left_stack: list[int] = []
            while True:
                i = current_edge[left]
                end = start[left + 1]
                target = dist[left] + 1

                while i < end:
                    right = to[i]
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
            current_edge = start[:-1].copy()
            for left in range(self.n_left):
                if mate_left[left] == -1 and dfs(left, shortest):
                    self.size += 1

        self._solved = True
        return self.size

    def matching_edges(self) -> list[tuple[int, int]]:
        self.solve()
        return [
            (left, right)
            for left, right in enumerate(self.mate_left)
            if right != -1
        ]
