# competitive-verifier: TITLE DAG の最小本数点素パス被覆

from python.graph.matching.BipartiteMatching import BipartiteMatching


class DAGDisjointPathCover:
    """DAG の全頂点をちょうど1回ずつ被覆するパスの最小本数を O((n+m) sqrt(n)) 時間で求める
    内部でトポロジカルソートするので頂点順は任意

    使用例:
        g = DAGDisjointPathCover(n)
        for u, v in edges:
            g.add_edge(u, v)
        count = g.solve()  # 最小本数
        paths = g.paths()  # 各パスの頂点列
    """

    def __init__(self, n: int) -> None:
        """n 頂点の空の DAG を作る。"""
        assert n >= 0
        self._n = n
        self._edges: list[tuple[int, int]] = []
        self._used = False
        self._count = -1
        self._starts: list[int] = []
        self._next_edge: list[int] = []

    def add_edge(self, u: int, v: int) -> int:
        """有向辺を追加し辺IDを返す。多重辺可、solve 前のみ。償却 O(1)。"""
        if self._used:
            raise RuntimeError("call add_edge() before solve()")
        assert 0 <= u < self._n and 0 <= v < self._n
        i = len(self._edges)
        self._edges.append((u, v))
        return i

    def solve(self) -> int:
        """最小本数を返す。DAG でなければ ValueError。1回限定。"""
        if self._used:
            raise RuntimeError("solve() can only be called once")
        self._used = True
        n = self._n
        adj = [[] for _ in range(n)]
        indegree = [0] * n
        for u, v in self._edges:
            adj[u].append(v)
            indegree[v] += 1
        order = [v for v in range(n) if indegree[v] == 0]
        for u in order:
            for v in adj[u]:
                indegree[v] -= 1
                if indegree[v] == 0:
                    order.append(v)
        if len(order) != n:
            raise ValueError("graph must be a DAG")
        g = BipartiteMatching(n, n)
        for u, v in self._edges:
            g.add_edge(u, v)
        self._count = n - g.solve()
        has_prev = [False] * n
        self._next_edge = [-1] * n
        for i in g.matching_edge_ids():
            u, v = self._edges[i]
            has_prev[v] = True
            self._next_edge[u] = i
        self._starts = [v for v in range(n) if not has_prev[v]]
        return self._count

    def paths(self) -> list[list[int]]:
        """解の頂点列を独立なリストで返す。solve 成功後のみ。O(n)。"""
        return self._paths(False)

    def edge_paths(self) -> list[list[int]]:
        """paths と同順の辺ID列。単頂点パスは空列。solve 成功後のみ。O(n)。"""
        return self._paths(True)

    def _paths(self, edge_ids: bool) -> list[list[int]]:
        if self._count < 0:
            raise RuntimeError("call solve() before paths()")
        result = []
        for v in self._starts:
            path = [] if edge_ids else [v]
            while self._next_edge[v] != -1:
                i = self._next_edge[v]
                v = self._edges[i][1]
                path.append(i if edge_ids else v)
            result.append(path)
        return result
