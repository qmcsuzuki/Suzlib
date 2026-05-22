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
        """
        トレイル分解を構成する。

        通常は dummy 辺を deficit -> surplus に追加して次数を揃え、
        オイラー閉路を作って dummy 辺で分割する。

        ただし、すでにオイラー路型
            len(surplus) == len(deficit) == 1
        の場合は dummy を張らず、outdeg - indeg = 1 の頂点から
        直接 Hierholzer を始める。
        """
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

        direct_start = -1

        if len(surplus) == 1 and len(deficit) == 1:
            # オイラー路型。dummy を張らず、正しい始点から直接始める。
            direct_start = surplus[0]
        else:
            # 一般の trail decomposition 用。
            # deficit 側から surplus 側へ dummy 辺を張る。
            for i in range(len(surplus)):
                aug_edges.append((deficit[i], surplus[i]))

        g = [[] for _ in range(self.n)]
        for eid, (u, _) in enumerate(aug_edges):
            g[u].append(eid)

        if lexicographically_min:
            base = len(aug_edges)
            for v in range(self.n):
                g[v].sort(
                    key=lambda eid: aug_edges[eid][1] * base + eid,
                    reverse=True,
                )
        else:
            for v in range(self.n):
                g[v].reverse()

        trails = []

        # オイラー路型の場合は、まず out-in=1 の頂点から 1 本取り出す。
        if direct_start != -1 and g[direct_start]:
            tr = self._find_euler_cycle(direct_start, g, aug_edges)
            trails.extend(self._split_cycle_by_dummy(tr, dummy_start))

        # 残った辺を通常通り回収する。
        # 非連結成分や、Eulerian trail が存在しない場合の余りはここに出る。
        for v in range(self.n):
            while g[v]:
                tr = self._find_euler_cycle(v, g, aug_edges)
                trails.extend(self._split_cycle_by_dummy(tr, dummy_start))

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

        first_dummy = -1
        for i, eid in enumerate(cycle):
            if eid >= dummy_start:
                first_dummy = i
                break

        if first_dummy == -1:
            return [cycle]

        # 閉路は循環列なので、先頭/末尾をまたぐ実辺列を 1 本に保つため
        # 最初のダミー辺の直後を先頭に回転してから分割する。
        rot = cycle[first_dummy + 1 :] + cycle[:first_dummy]

        res = []
        cur = []
        for eid in rot:
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
            # 辺が 0 本のときは、長さ 0 のトレイルとして頂点 1 つを返す。
            # (verify 問題では頂点列の長さが m+1 を満たす必要がある)
            return True, [0] if self.n else [], []
        if len(self._trails) != 1:
            return False, [], []

        tr = self._trails[0]
        vs = [self.edges[tr[0]][0]]
        for eid in tr:
            vs.append(self.edges[eid][1])
        return True, vs, tr

    def eulerian_circuit(self):
        if len(self._trails) == 0:
            return True, [0] if self.n else [], []
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
