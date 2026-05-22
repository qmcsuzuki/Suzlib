# competitive-verifier: TITLE 無向トレイル分解、オイラーパス (undirected Eulerian path/circuit)

class UndirectedTrailDecomposition:
    def __init__(self, n, edges, lexicographically_min=False):
        self.n = n
        self.edges = list(edges)
        self.m = len(edges)

        self.deg = [0] * n
        for u, v in self.edges:
            if u == v:
                self.deg[u] += 2
            else:
                self.deg[u] += 1
                self.deg[v] += 1

        # _orient[eid] = (実際に通った始点, 実際に通った終点)
        # 無向辺なので、eulerian_trail などで頂点列を復元するために必要。
        self._orient = [None] * self.m
        self._trails = self._build_trails(lexicographically_min)

    def _build_trails(self, lexicographically_min):
        """
        トレイル分解を構成する。

        通常は奇次数頂点同士に dummy 辺を追加して次数を偶数にし、
        オイラー閉路を作って dummy 辺で分割する。
        ただし、すでにオイラー路型
            len(odd) == 2
        の場合は dummy を張らず、奇次数頂点から直接 Hierholzer を始める。
        """
        aug_edges = list(self.edges)
        dummy_start = len(aug_edges)

        odd = []
        for v in range(self.n):
            if self.deg[v] & 1:
                odd.append(v)

        direct_start = -1
        if len(odd) == 2:
            # オイラー路型。dummy を張らず、奇次数頂点から直接始める。
            direct_start = odd[0]
        else:
            # 一般の trail decomposition 用。
            # 奇次数頂点同士に dummy 辺を張る。
            for i in range(0, len(odd), 2):
                aug_edges.append((odd[i], odd[i + 1]))

        g = [[] for _ in range(self.n)]
        for eid, (u, v) in enumerate(aug_edges):
            g[u].append((eid, v))
            g[v].append((eid, u))

        if lexicographically_min:
            base = len(aug_edges)
            for v in range(self.n):
                g[v].sort(
                    key=lambda p: p[1] * base + p[0],
                    reverse=True,
                )
        else:
            for v in range(self.n):
                g[v].reverse()

        used = [False] * len(aug_edges)
        orient = [None] * len(aug_edges)
        trails = []

        # オイラー路型の場合は、まず奇次数頂点から 1 本取り出す。
        if direct_start != -1:
            self._discard_used(g, used, direct_start)
            if g[direct_start]:
                tr = self._find_euler_cycle(direct_start, g, used, orient)
                trails.extend(self._split_cycle_by_dummy(tr, dummy_start))

        # 残った辺を通常通り回収する。
        # 非連結成分や、Eulerian trail が存在しない場合の余りはここに出る。
        for v in range(self.n):
            while True:
                self._discard_used(g, used, v)
                if not g[v]:
                    break
                tr = self._find_euler_cycle(v, g, used, orient)
                trails.extend(self._split_cycle_by_dummy(tr, dummy_start))

        for eid in range(self.m):
            self._orient[eid] = orient[eid]

        return trails

    def _discard_used(self, g, used, v):
        while g[v] and used[g[v][-1][0]]:
            g[v].pop()

    def _find_euler_cycle(self, start, g, used, orient):
        """start を含む 1 本のオイラー閉路/路(辺列)を返す。"""
        st_v = [start]
        st_e = []
        cycle = []

        while st_v:
            v = st_v[-1]
            self._discard_used(g, used, v)

            if g[v]:
                eid, to = g[v].pop()
                if used[eid]:
                    continue
                used[eid] = True
                orient[eid] = (v, to)
                st_e.append(eid)
                st_v.append(to)
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
        # 最初の dummy 辺の直後を先頭に回転してから分割する。
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
        vs = [self._orient[tr[0]][0]]
        for eid in tr:
            vs.append(self._orient[eid][1])
        return True, vs, tr

    def eulerian_circuit(self):
        if len(self._trails) == 0:
            return True, [0] if self.n else [], []
        if len(self._trails) != 1:
            return False, [], []

        tr = self._trails[0]
        if self._orient[tr[0]][0] != self._orient[tr[-1]][1]:
            return False, [], []

        vs = [self._orient[tr[0]][0]]
        for eid in tr:
            vs.append(self._orient[eid][1])
        return True, vs, tr

    def min_add_to_euler_path(self):
        k = len(self._trails)
        if k == 0:
            return 0, []

        add = []
        for i in range(k - 1):
            u = self._orient[self._trails[i][-1]][1]
            v = self._orient[self._trails[i + 1][0]][0]
            add.append((u, v))
        return k - 1, add

    def min_add_to_euler_circuit(self):
        k = len(self._trails)
        if k == 0:
            return 0, []
        if k == 1:
            tr = self._trails[0]
            if self._orient[tr[0]][0] == self._orient[tr[-1]][1]:
                return 0, []

        add = []
        for i in range(k):
            u = self._orient[self._trails[i][-1]][1]
            v = self._orient[self._trails[(i + 1) % k][0]][0]
            add.append((u, v))
        return k, add
