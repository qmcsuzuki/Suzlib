# competitive-verifier: TITLE 有向トレイル分解、オイラーパス (directed Eulerian path/circuit)


class DirectedTrailDecomposition:
    def __init__(self, n, edges, lexicographically_min=False):
        self.n = n
        self.edges = list(edges)
        self.m = len(edges)

        self.indeg = [0] * n
        self.outdeg = [0] * n

        for u, v in self.edges:
            self.outdeg[u] += 1
            self.indeg[v] += 1

        self._trails = self._build_trails(lexicographically_min)

    def _build_trails(self, lexicographically_min):
        """ダミー辺で次数を揃えてオイラー閉路を作り、ダミー辺で分割してトレイル分解する。"""
        aug_edges = list(self.edges)
        dummy_start = len(aug_edges)

        surplus = []
        deficit = []
        for v in range(self.n):
            d = self.outdeg[v] - self.indeg[v]
            if d > 0:
                surplus.extend([v] * d)
            elif d < 0:
                deficit.extend([v] * (-d))

        # 不足側(deficit) -> 余剰側(surplus)にダミー辺を張ると全頂点の入出次数が一致する。
        for i in range(len(surplus)):
            aug_edges.append((deficit[i], surplus[i]))

        g = [[] for _ in range(self.n)]
        for eid, (u, _) in enumerate(aug_edges):
            g[u].append(eid)

        if lexicographically_min:
            for v in range(self.n):
                g[v].sort(key=lambda eid: (aug_edges[eid][1], eid), reverse=True)
        else:
            for v in range(self.n):
                g[v].reverse()  # 辺番号の小さい順に pop する

        trails = []
        for v in range(self.n):
            while g[v]:
                cyc = self._find_euler_cycle(v, g, aug_edges)
                trails.extend(self._split_cycle_by_dummy(cyc, dummy_start))
        return trails

    def _find_euler_cycle(self, start, g, edges):
        """start を含む 1 本のオイラー閉路(辺列)を返す。"""
        st_v = [start]
        st_e = []
        cycle = []

        while st_v:
            v = st_v[-1]
            if g[v]:
                eid = g[v].pop()
                st_e.append(eid)
                st_v.append(edges[eid][1])
            else:
                st_v.pop()
                if st_e:
                    cycle.append(st_e.pop())

        cycle.reverse()
        return cycle

    def _split_cycle_by_dummy(self, cycle, dummy_start):
        """閉路の辺列をダミー辺で切って、元グラフのトレイル列に戻す。"""
        if not cycle:
            return []

        has_dummy = False
        for eid in cycle:
            if eid >= dummy_start:
                has_dummy = True
                break

        if not has_dummy:
            return [cycle]

        res = []
        cur = []
        for eid in cycle:
            if eid >= dummy_start:
                if cur:
                    res.append(cur)
                    cur = []
            else:
                cur.append(eid)
        if cur:
            res.append(cur)

        return res

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
