# competitive-verifier: TITLE 最大二部マッチング（自動二部彩色）

from python.graph.matching.BipartiteMatching import BipartiteMatching


class GeneralBipartiteMatching:
    """頂点を一つの整数空間で与え、自動で二部彩色する最大二部マッチング。
    内部で左右型の BipartiteMatching に帰着する（color 0 を左、color 1 を右）。
    solve 後も add_edge でき、次の solve で彩色から作り直す（O(n + m) + マッチング）。

    公開属性（solve 後に有効）:
      color[v]       : 自動二部彩色。0 が左、1 が右
      from_left[i]   : lr_matching() の左 i に対応する元の頂点
      from_right[j]  : lr_matching() の右 j に対応する元の頂点
      size           : 最大マッチングの大きさ
    """

    def __init__(self, n: int) -> None:
        """n 頂点の空の辺列と、未彩色・未マッチの状態を初期化する。"""
        assert 0 <= n
        self.n = n
        self._edges: list[tuple[int, int]] = []
        self.color = [-1] * n
        self._to_left = [-1] * n
        self._to_right = [-1] * n
        self.from_left: list[int] = []
        self.from_right: list[int] = []
        self._mate = [-1] * n
        self.size = 0
        self._matching: BipartiteMatching | None = None
        self._solved = False

    def add_edge(self, u: int, v: int) -> int:
        """頂点 u, v を結ぶ辺を追加し、辺番号を返す。solve 後は彩色を含めて再構築する。"""
        assert 0 <= u < self.n
        assert 0 <= v < self.n
        edge_id = len(self._edges)
        self._edges.append((u, v))
        self._solved = False
        return edge_id

    def edge_count(self) -> int:
        """これまでに追加した辺の本数を返す。"""
        return len(self._edges)

    def edges(self) -> list[tuple[int, int, int]]:
        """追加した辺を (edge_id, u, v) で追加順に返す。"""
        return [(edge_id, u, v) for edge_id, (u, v) in enumerate(self._edges)]

    def _bipartition(self) -> None:
        """現在の辺集合を二部彩色し、各頂点の色を self.color に保存する。"""
        graph = [[] for _ in range(self.n)]
        for u, v in self._edges:
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
        self.from_left = [v for v in range(self.n) if self.color[v] == 0]
        self.from_right = [v for v in range(self.n) if self.color[v] == 1]
        self._to_left = [-1] * self.n
        self._to_right = [-1] * self.n
        for left, v in enumerate(self.from_left):
            self._to_left[v] = left
        for right, v in enumerate(self.from_right):
            self._to_right[v] = right

        matching = BipartiteMatching(len(self.from_left), len(self.from_right))
        for u, v in self._edges:
            if self.color[u] == 0:
                matching.add_edge(self._to_left[u], self._to_right[v])
            else:
                matching.add_edge(self._to_left[v], self._to_right[u])
        self._matching = matching

    def solve(self) -> int:
        """現在のグラフの最大マッチング数を返す。非二部グラフなら ValueError。"""
        if self._solved:
            return self.size
        self._build_lr()
        assert self._matching is not None
        self.size = self._matching.solve()
        self._mate = [-1] * self.n
        for left, right in enumerate(self._matching.mate_left):
            if right == -1:
                continue
            u = self.from_left[left]
            v = self.from_right[right]
            self._mate[u] = v
            self._mate[v] = u
        self._solved = True
        return self.size

    def lr_matching(self) -> BipartiteMatching:
        """solve 後の内部の左右型マッチングを返す。辺番号は入力時と同じ。
        左 i は元の頂点 from_left[i]、右 j は元の頂点 from_right[j] に対応する（color 0 が左）。
        """
        self.solve()
        assert self._matching is not None
        return self._matching

    def matching_edges(self) -> list[tuple[int, int]]:
        """最大マッチングを (色0の頂点, 色1の頂点) の組で返す。"""
        self.solve()
        assert self._matching is not None
        return [
            (self.from_left[left], self.from_right[right])
            for left, right in enumerate(self._matching.mate_left)
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
        return self._mate.copy()

    def residual_graph(self, middle_capacity_inf: bool = False) -> list[list[int]]:
        """
        自動二部彩色で color 0 を左、color 1 を右とした残余グラフを返す。

        頂点番号は入力時の 0..n-1 を保ち、s = n、t = n+1 とする。
        middle_capacity_inf=True なら左から右への容量を inf とみなす。
        """
        self.solve()
        assert self._matching is not None
        rg = self._matching.residual_graph(middle_capacity_inf)
        original = self.from_left + self.from_right
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
        return [self.from_left[v] for v in left] + [self.from_right[v] for v in right]

    def max_independent_set(self) -> list[int]:
        """元の頂点番号で最大独立集合を返す。"""
        self.solve()
        assert self._matching is not None
        left, right = self._matching.max_independent_set()
        return [self.from_left[v] for v in left] + [self.from_right[v] for v in right]
