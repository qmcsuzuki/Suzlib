# CSR matching experiments: old HopcoftKarp-style full-layer phases.

from python.graph.BipartiteMatching import BipartiteMatching


class BipartiteMatchingAggressive(BipartiteMatching):
    """Current CSR/degree-greedy front end with old-style aggressive phases."""

    def solve(self) -> int:
        if self._solved:
            return self.size

        self._build_csr()
        start = self._start
        to = self._to
        mate_left = self.mate_left
        mate_right = self.mate_right
        n_left = self.n_left

        if self.size == 0:
            self.size = self._degree_greedy()
            if self.size == 0:
                self._solved = True
                return 0
            if self.size == min(self.n_left, self.n_right):
                self._solved = True
                return self.size

        inf = n_left + 1
        dist = [inf] * n_left
        current_edge = [0] * n_left

        def bfs() -> bool:
            queue = [0] * n_left
            ql = 0
            qr = 0
            for left in range(n_left):
                if mate_left[left] == -1:
                    dist[left] = 0
                    queue[qr] = left
                    qr += 1
                else:
                    dist[left] = inf

            found = False
            while ql < qr:
                left = queue[ql]
                ql += 1
                next_dist = dist[left] + 1
                for i in range(start[left], start[left + 1]):
                    right = to[i]
                    next_left = mate_right[right]
                    if next_left == -1:
                        found = True
                    elif dist[next_left] == inf:
                        dist[next_left] = next_dist
                        queue[qr] = next_left
                        qr += 1
            return found

        def dfs(start_left: int) -> bool:
            left = start_left
            left_stack = []
            right_stack = []
            while True:
                i = current_edge[left]
                end = start[left + 1]
                target = dist[left] + 1
                while i < end:
                    right = to[i]
                    i += 1
                    next_left = mate_right[right]
                    if next_left == -1:
                        current_edge[left] = i
                        left_stack.append(left)
                        right_stack.append(right)
                        while left_stack:
                            u = left_stack.pop()
                            v = right_stack.pop()
                            mate_left[u] = v
                            mate_right[v] = u
                        return True
                    if dist[next_left] == target:
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

        while bfs():
            current_edge[:] = start[:-1]
            for left in range(n_left):
                if mate_left[left] == -1 and dfs(left):
                    self.size += 1

        self._solved = True
        return self.size


class BipartiteMatchingAggressiveRaw(BipartiteMatching):
    """Direct CSR + old-style aggressive phases, without degree greedy."""

    def solve(self) -> int:
        if self._solved:
            return self.size

        self._build_csr()
        start = self._start
        to = self._to
        mate_left = self.mate_left
        mate_right = self.mate_right
        n_left = self.n_left
        inf = n_left + 1
        dist = [inf] * n_left
        current_edge = [0] * n_left

        def bfs() -> bool:
            queue = [0] * n_left
            ql = 0
            qr = 0
            for left in range(n_left):
                if mate_left[left] == -1:
                    dist[left] = 0
                    queue[qr] = left
                    qr += 1
                else:
                    dist[left] = inf

            found = False
            while ql < qr:
                left = queue[ql]
                ql += 1
                next_dist = dist[left] + 1
                for i in range(start[left], start[left + 1]):
                    right = to[i]
                    next_left = mate_right[right]
                    if next_left == -1:
                        found = True
                    elif dist[next_left] == inf:
                        dist[next_left] = next_dist
                        queue[qr] = next_left
                        qr += 1
            return found

        def dfs(start_left: int) -> bool:
            left = start_left
            left_stack = []
            right_stack = []
            while True:
                i = current_edge[left]
                end = start[left + 1]
                target = dist[left] + 1
                while i < end:
                    right = to[i]
                    i += 1
                    next_left = mate_right[right]
                    if next_left == -1:
                        current_edge[left] = i
                        left_stack.append(left)
                        right_stack.append(right)
                        while left_stack:
                            u = left_stack.pop()
                            v = right_stack.pop()
                            mate_left[u] = v
                            mate_right[v] = u
                        return True
                    if dist[next_left] == target:
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

        while bfs():
            current_edge[:] = start[:-1]
            for left in range(n_left):
                if mate_left[left] == -1 and dfs(left):
                    self.size += 1

        self._solved = True
        return self.size
