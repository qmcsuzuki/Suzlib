# https://atcoder.jp/contests/abc445/submissions/73385137

from collections import deque
class HopcroftKarp:
    """
    二部グラフのマッチング、最大独立集合など
    内部でやること: 二部彩色 -> L/R詰め直し -> Hopcroft-Karp -> 派生量
    - max_matching(nL,nR,X2Y): （内部関数）二部グラフの左右からマッチングを計算

    関数
    - HK.add_edge(u,v): （無向）辺追加
    - HK.solve(): 最大マッチングの値を返す
    - HK.matching_edges(): マッチングされた辺の集合を返す
    - HK.min_vertex_cover(): 最小頂点被覆に使われる点集合のリストを返す
    - HK.max_independent_set(): 最大独立集合に使われる点集合のリストを返す
    """
    # 二部グラフの左右からマッチングを計算 (Hopcroft Karp)
    @classmethod
    def max_matching(cls, nL: int, nR: int, X2Y: list[list[int]]) -> tuple[int, list[int], list[int]]:
        mateL: list[int] = [-1] * nL
        mateR: list[int] = [-1] * nR
        dist: list[int] = [0] * nL
        it: list[int] = [0] * nL # it[v]: 左側の頂点 v から伸びる辺でまだ見てない番号の最小値（イテレータの位置）
        INF = nL + 5

        def bfs() -> bool: # 最短路の計算
            q = deque()
            for u in range(nL):
                if mateL[u] == -1:
                    dist[u] = 0
                    q.append(u)
                else:
                    dist[u] = INF

            found = False
            while q:
                u = q.popleft()
                du = dist[u]
                for v in X2Y[u]:
                    w = mateR[v]
                    if w == -1:
                        found = True
                    elif dist[w] == INF:
                        dist[w] = du + 1
                        q.append(w)
            return found

        def dfs_iter(u: int) -> bool: # 最短パスをとれるだけとる
            stack: list[int] = []
            choice: list[int] = []
            while True:
                i = it[u]
                adj = X2Y[u]

                while i < len(adj):
                    v = adj[i]
                    i += 1
                    w = mateR[v]

                    if w == -1:
                        it[u] = i
                        stack.append(u)
                        choice.append(v)
                        while stack:
                            uu = stack.pop()
                            vv = choice.pop()
                            mateL[uu] = vv
                            mateR[vv] = uu
                        return True

                    if dist[w] == dist[u] + 1:
                        it[u] = i
                        stack.append(u)
                        choice.append(v)
                        u = w
                        break
                else:
                    it[u] = i
                    dist[u] = INF
                    if not stack:
                        return False
                    u = stack.pop()
                    choice.pop()

            return False

        flow = 0
        while bfs():
            for u in range(nL):
                it[u] = 0
            for u in range(nL):
                if mateL[u] == -1 and dfs_iter(u):
                    flow += 1

        return flow, mateL, mateR

    # ---------- インスタンス（ビルド＋派生量） ----------
    def __init__(self, n: int):
        self.n = n
        self.edges: list[tuple[int, int]] = []  # 無向辺を1本だけ保持

        self.color: list[int] = [-1] * n

        self.toL: list[int] = []
        self.toR: list[int] = []
        self.fromL: list[int] = []
        self.fromR: list[int] = []

        self.X2Y: list[list[int]] = []

        self.size = 0
        self.mate: list[int] = [-1] * n
        self.mateL: list[int] = []
        self.mateR: list[int] = []

        self._solved = False

    def add_edge(self, u: int, v: int) -> None:
        self.edges.append((u, v))
        self._solved = False

    def _bipartition(self) -> None:
        g: list[list[int]] = [[] for _ in range(self.n)]
        for u, v in self.edges:
            if u == v:
                raise ValueError("self-loop: graph is not bipartite")
            g[u].append(v)
            g[v].append(u)

        color = self.color
        for i in range(self.n):
            color[i] = -1

        q = deque()
        for s in range(self.n):
            if color[s] != -1:
                continue
            color[s] = 0
            q.append(s)
            while q:
                u = q.popleft()
                cu = color[u]
                for v in g[u]:
                    cv = color[v]
                    if cv == -1:
                        color[v] = cu ^ 1
                        q.append(v)
                    elif cv == cu:
                        raise ValueError("graph is not bipartite")

    def _build_lr(self) -> None:
        n = self.n
        self.toL = [-1] * n
        self.toR = [-1] * n
        self.fromL = []
        self.fromR = []

        for u, c in enumerate(self.color):
            if c == 0:
                self.toL[u] = len(self.fromL)
                self.fromL.append(u)
            else:
                self.toR[u] = len(self.fromR)
                self.fromR.append(u)

        self.X2Y = [[] for _ in range(len(self.fromL))]
        for u, v in self.edges:
            if self.color[u] == 0:
                self.X2Y[self.toL[u]].append(self.toR[v])
            else:
                self.X2Y[self.toL[v]].append(self.toR[u])

    def solve(self) -> int:
        if self._solved:
            return self.size

        self._bipartition()
        self._build_lr()

        self.size, self.mateL, self.mateR = self.max_matching(len(self.fromL), len(self.fromR), self.X2Y)

        mate = [-1] * self.n
        for uL, vR in enumerate(self.mateL):
            if vR != -1:
                u = self.fromL[uL]
                v = self.fromR[vR]
                mate[u] = v
                mate[v] = u
        self.mate = mate

        self._solved = True
        return self.size

    def matching_edges(self) -> list[tuple[int, int]]:
        self.solve()
        res: list[tuple[int, int]] = []
        for u in range(self.n):
            v = self.mate[u]
            if v != -1 and u < v and self.color[u] == 0:
                res.append((u, v))
        return res

    def _reachable_sets(self) -> tuple[list[bool], list[bool]]:
        """
        未マッチ左から交互路で到達できる集合 ZL, ZR を計算。
        キューは左頂点のみ。
          - 左 u からは「非マッチ辺」u->v を辿って右 v を訪れる
          - 右 v を訪れたら（v がマッチ済みなら）「マッチ辺」v->mateR[v] で左へ戻る
        """
        self.solve()
        nL = len(self.fromL)
        nR = len(self.fromR)

        visL = [False] * nL
        visR = [False] * nR
        q = deque()

        # 始点：未マッチの左
        for u in range(nL):
            if self.mateL[u] == -1:
                visL[u] = True
                q.append(u)

        while q:
            u = q.popleft()
            mu = self.mateL[u]
            for v in self.X2Y[u]:
                if v == mu:
                    continue  # 非マッチ辺のみ
                if visR[v]:
                    continue
                visR[v] = True
                w = self.mateR[v]  # マッチ辺で左へ（存在すれば）
                if w != -1 and not visL[w]:
                    visL[w] = True
                    q.append(w)

        return visL, visR

    def min_vertex_cover(self) -> list[int]:
        self.solve()
        visL, visR = self._reachable_sets()

        cover: list[int] = []
        for uL, u in enumerate(self.fromL):
            if not visL[uL]:
                cover.append(u)
        for vR, v in enumerate(self.fromR):
            if visR[vR]:
                cover.append(v)
        return cover

    def max_independent_set(self) -> list[int]:
        self.solve()
        visL, visR = self._reachable_sets()

        indep: list[int] = []
        for uL, u in enumerate(self.fromL):
            if visL[uL]:
                indep.append(u)
        for vR, v in enumerate(self.fromR):
            if not visR[vR]:
                indep.append(v)
        return indep

