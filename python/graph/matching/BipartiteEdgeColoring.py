# competitive-verifier: TITLE 二部多重グラフの最小辺彩色

from python.graph.UndirectedTrailDecomposition import UndirectedTrailDecomposition


class BipartiteEdgeColoring:
    """二部多重グラフを最大次数 Delta 個のマッチングに分解する (Alon--Gabow 法)。

    頂点は左右で別々に 0-indexed。多重辺を許し、入力辺番号を維持する。
    Hierholzer 法による偶数正則グラフの半分割と、多重度を利用した
    完全マッチング構築により、V = n_left + n_right, E = 辺数として
    O(V + E log(E + 1)) 時間、O(V + E) 空間。

    使用例:
        g = BipartiteEdgeColoring(n_left, n_right)
        for u, v in edges:
            g.add_edge(u, v)
        k = g.solve()             # 必要な最小色数 (= 最大次数)
        colors = g.edge_colors()  # 辺番号順に 0, ..., k-1
    """

    def __init__(self, n_left: int, n_right: int) -> None:
        """左右の頂点数を指定して初期化する。"""
        assert n_left >= 0 and n_right >= 0
        self.n_left = n_left
        self.n_right = n_right
        self._edges: list[tuple[int, int]] = []
        self._solved = False
        self._degree = 0
        self._colors: list[int] = []
        self._classes: list[list[int]] = []

    def add_edge(self, left: int, right: int) -> int:
        """二部辺を追加し、入力順の辺番号を返す。solve 前のみ。"""
        if self._solved:
            raise RuntimeError("call add_edge() before solve()")
        assert 0 <= left < self.n_left and 0 <= right < self.n_right
        eid = len(self._edges)
        self._edges.append((left, right))
        return eid

    @staticmethod
    def _pack_vertices(degrees: list[int], degree: int) -> tuple[list[int], list[int]]:
        """次数の合計が degree 以下になるよう同じ側の頂点をまとめる。"""
        group = [-1] * len(degrees)
        loads = []
        for v, d in enumerate(degrees):
            if d == 0:
                continue
            if not loads or loads[-1] + d > degree:
                loads.append(0)
            group[v] = len(loads) - 1
            loads[-1] += d
        return group, loads

    def _halve(self, edge_ids: list[int]) -> tuple[list[int], list[int]]:
        """偶数正則二部グラフを、等しい次数の二部グラフ2個に分割する。"""
        n = self._n
        graph = UndirectedTrailDecomposition(
            2 * n,
            [(self._left[e], n + self._right[e]) for e in edge_ids],
        )
        first, second = [], []
        for trail in graph.trail_decomposition():
            for i, local_id in enumerate(trail):
                if i & 1:
                    second.append(edge_ids[local_id])
                else:
                    first.append(edge_ids[local_id])
        return first, second

    def _perfect_matching(self, edge_ids: list[int], degree: int) -> list[int]:
        """正則二部グラフの完全マッチングを、辺の多重度付き半分割のみで得る。"""
        n = self._n
        m = n * degree
        power = 1 << (m - 1).bit_length()
        alpha, beta = divmod(power, degree)

        # 負の辺番号 -(v+1) は左 v と右 v を結ぶ人工辺。
        ids = edge_ids.copy()
        counts = [alpha] * len(ids)
        if beta:
            ids.extend(-v - 1 for v in range(n))
            counts.extend([beta] * n)

        for _ in range(power.bit_length() - 1):
            first = [c >> 1 for c in counts]
            second = first.copy()
            odd_edges = []
            odd_indices = []
            for i, (e, c) in enumerate(zip(ids, counts)):
                if not (c & 1):
                    continue
                if e >= 0:
                    u, v = self._left[e], self._right[e]
                else:
                    u = v = -e - 1
                odd_edges.append((u, n + v))
                odd_indices.append(i)

            if odd_edges:
                graph = UndirectedTrailDecomposition(2 * n, odd_edges)
                for trail in graph.trail_decomposition():
                    for j, local_id in enumerate(trail):
                        i = odd_indices[local_id]
                        if j & 1:
                            second[i] += 1
                        else:
                            first[i] += 1

            bad_first = sum(c for e, c in zip(ids, first) if e < 0)
            bad_second = sum(c for e, c in zip(ids, second) if e < 0)
            chosen = first if bad_first <= bad_second else second
            new_ids, new_counts = [], []
            for e, c in zip(ids, chosen):
                if c:
                    new_ids.append(e)
                    new_counts.append(c)
            ids, counts = new_ids, new_counts

        # 人工辺の総数は n * beta < power。半減を繰り返すと 0 になる。
        assert len(ids) == n and all(e >= 0 and c == 1 for e, c in zip(ids, counts))
        return ids

    def _color_power_of_two(self, edge_ids: list[int], degree: int) -> list[list[int]]:
        """2冪正則二部グラフを Euler 半分割のみで彩色する。"""
        if degree == 1:
            return [edge_ids]
        a, b = self._halve(edge_ids)
        half = degree >> 1
        return self._color_power_of_two(a, half) + self._color_power_of_two(b, half)

    def _color_regular(self, edge_ids: list[int], degree: int) -> list[list[int]]:
        """正則二部グラフを degree 個の完全マッチングに分解する。"""
        if degree == 1:
            return [edge_ids]
        if degree & 1:
            matching = self._perfect_matching(edge_ids, degree)
            matched = set(matching)
            remaining = [e for e in edge_ids if e not in matched]
            return [matching] + self._color_regular(remaining, degree - 1)

        a, b = self._halve(edge_ids)
        half = degree >> 1
        classes = self._color_regular(a, half)
        power = 1 << (half - 1).bit_length()
        extra = power - half
        for cls in classes[:extra]:
            b.extend(cls)
        return classes[extra:] + self._color_power_of_two(b, power)

    def solve(self) -> int:
        """最大次数 (= 最小辺彩色数) を返す。結果は繰り返し参照できる。"""
        if self._solved:
            return self._degree

        left_degree = [0] * self.n_left
        right_degree = [0] * self.n_right
        for u, v in self._edges:
            left_degree[u] += 1
            right_degree[v] += 1
        degree = max(max(left_degree, default=0), max(right_degree, default=0))
        self._degree = degree
        if degree == 0:
            self._solved = True
            return 0

        # 低次数の頂点を同じ側で結合し、正則化後の辺数を O(E) に保つ。
        left_group, left_load = self._pack_vertices(left_degree, degree)
        right_group, right_load = self._pack_vertices(right_degree, degree)
        n = max(len(left_load), len(right_load))
        left_load.extend([0] * (n - len(left_load)))
        right_load.extend([0] * (n - len(right_load)))
        self._n = n
        self._left = [left_group[u] for u, _ in self._edges]
        self._right = [right_group[v] for _, v in self._edges]

        # 左右で足りない次数を多重辺で埋めて degree-正則にする。
        i = j = 0
        missing_left = [degree - d for d in left_load]
        missing_right = [degree - d for d in right_load]
        while i < n and j < n:
            if missing_left[i] == 0:
                i += 1
                continue
            if missing_right[j] == 0:
                j += 1
                continue
            count = min(missing_left[i], missing_right[j])
            self._left.extend([i] * count)
            self._right.extend([j] * count)
            missing_left[i] -= count
            missing_right[j] -= count

        classes = self._color_regular(list(range(len(self._left))), degree)
        m = len(self._edges)
        self._colors = [-1] * m
        self._classes = [[] for _ in range(degree)]
        for color, matching in enumerate(classes):
            for e in matching:
                if e < m:
                    self._colors[e] = color
                    self._classes[color].append(e)
        self._solved = True
        return degree

    def edge_colors(self) -> list[int]:
        """各入力辺の色 (0 以上 Delta 未満) を辺番号順に返す。"""
        if not self._solved:
            raise RuntimeError("call solve() before edge_colors()")
        return self._colors.copy()

    def color_classes(self) -> list[list[int]]:
        """各色に属する入力辺番号を返す。各色クラスはマッチング。"""
        if not self._solved:
            raise RuntimeError("call solve() before color_classes()")
        return [cls.copy() for cls in self._classes]
