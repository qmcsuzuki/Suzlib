# competitive-verifier: TITLE 有向トレイル分解、オイラーパス (directed Eulerian path/circuit)


class DirectedTrailDecomposition:
    def __init__(self, n, edges, lexicographically_min=False):
        self.n = n
        self.edges = list(edges)
        self.m = len(edges)

        self.indeg = [0] * n
        self.outdeg = [0] * n
        self._g = [[] for _ in range(n)]

        for eid, (u, v) in enumerate(self.edges):
            self.outdeg[u] += 1
            self.indeg[v] += 1
            self._g[u].append(eid)

        if lexicographically_min:
            for v in range(n):
                self._g[v].sort(
                    key=lambda eid: (self.edges[eid][1], eid),
                    reverse=True,
                )
        else:
            for v in range(n):
                self._g[v].reverse() # 辺番号の小さい順に pop することになる

        self._trails = []
        for v in range(n):
            for _ in range(max(0, self.outdeg[v] - self.indeg[v])):
                self._trails.append(self._find_trail(v))

        for v in range(n):
            while self._g[v]:
                self._trails.append(self._find_trail(v))

    def _find_trail(self, start):
        """
        start から始まる maximal directed trail を 1 本返す。
        self._g を破壊する。
        return: list[int]  # edge ids
        """
        ...


    def trail_decomposition(self):
        return self._trails

    def eulerian_trail(self):
        if len(self._trails) == 0:
            return True, [], []
        if len(self._trails) != 1:
            return False, [], []

        tr = self._trails[0]
        vs = [self.edges[tr[0]][0]]
        for eid in tr:
            vs.append(self.edges[eid][1])
        return True, vs, tr

    def eulerian_circuit(self):
        if len(self._trails) == 0:
            return True, [], []
        if len(self._trails) != 1:
            return False, [], []

        tr = self._trails[0]
        if self.edges[tr[0]][0] != self.edges[tr[-1]][1]:
            return False, [], []

        vs = [self.edges[tr[0]][0]]
        for eid in tr:
            vs.append(self.edges[eid][1])
        return True, vs, tr

    def min_add_to_euler_path(self):
        k = len(self._trails)
        if k == 0:
            return 0, []

        add = []
        for i in range(k - 1):
            u = self.edges[self._trails[i][-1]][1]
            v = self.edges[self._trails[i + 1][0]][0]
            add.append((u, v))
        return k - 1, add

    def min_add_to_euler_circuit(self):
        k = len(self._trails)
        if k == 0:
            return 0, []

        if k == 1:
            tr = self._trails[0]
            if self.edges[tr[0]][0] == self.edges[tr[-1]][1]:
                return 0, []

        add = []
        for i in range(k):
            u = self.edges[self._trails[i][-1]][1]
            v = self.edges[self._trails[(i + 1) % k][0]][0]
            add.append((u, v))
        return k, add
