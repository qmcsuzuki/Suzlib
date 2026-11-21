# competitive-verifier: TITLE 最大二部マッチング（自動二部彩色）

from python.graph.matching.BipartiteMatching import BipartiteMatching


class GeneralBipartiteMatching:
    """頂点を一つの整数空間で与え、自動で二部彩色する最大二部マッチング。"""

    def __init__(self, n: int) -> None:
        """n 頂点の空の辺列と、未彩色・未マッチの状態を初期化する。"""
        assert 0 <= n
        self.n = n
        self.edges: list[tuple[int, int]] = []
        self.color = [-1] * n
        self.toL = [-1] * n
        self.toR = [-1] * n
        self.fromL: list[int] = []
        self.fromR: list[int] = []
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

        matching = BipartiteMatching(len(self.fromL), len(self.fromR))
        for u, v in self.edges:
            if self.color[u] == 0:
                matching.add_edge(self.toL[u], self.toR[v])
            else:
                matching.add_edge(self.toL[v], self.toR[u])
        self._matching = matching

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

    def lr_matching(self) -> BipartiteMatching:
        """solve 後の内部の左右型マッチングを返す。辺番号は入力時と同じ。
        左 i は元の頂点 fromL[i]、右 j は元の頂点 fromR[j] に対応する（color 0 が左）。
        """
        self.solve()
        assert self._matching is not None
        return self._matching

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

    def residual_graph(self, middle_capacity_inf: bool = False) -> list[list[int]]:
        """
        自動二部彩色で color 0 を左、color 1 を右とした残余グラフを返す。

        頂点番号は入力時の 0..n-1 を保ち、s = n、t = n+1 とする。
        middle_capacity_inf=True なら左から右への容量を inf とみなす。
        """
        self.solve()
        assert self._matching is not None
        rg = self._matching.residual_graph(middle_capacity_inf)
        original = self.fromL + self.fromR
        internal_s = self.n
        internal_t = self.n + 1
        original += [internal_s, internal_t]

        g = [[] for _ in range(self.n + 2)]
        for v, adj in enumerate(rg):
            g[original[v]] = [original[w] for w in adj]
        return g

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
