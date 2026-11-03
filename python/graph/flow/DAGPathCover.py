# competitive-verifier: TITLE DAG の最小パス被覆（点素・共有可）

from python.graph.flow.MaxFlow import MFGraph
from python.graph.matching.BipartiteMatching import BipartiteMatching


class DAGPathCover:
    """必須頂点を覆う最小本数の有向パスを求める。

    頂点番号は 0..n-1。solve の引数を省略すると全頂点が必須で、開始・終了も自由。
    vertex_disjoint=True は任意頂点を含めて点素、False はパス間の共有可。
    元の辺をたどり、単頂点パスも許す（開始・終了の両方が許可された場合）。
    多重辺と空グラフを許す。solve 時に DAG を検査し、閉路なら ValueError。
    solve は毎回、指定された条件で再構築する。前回の条件は引き継がない。

    使用例:
        g = DAGPathCover(3, vertex_disjoint=False)
        g.add_edge(0, 1)
        g.add_edge(1, 2)
        k = g.solve(required=[True, False, True])  # 1。実行不能なら -1
        paths = g.paths()   # [[0, 1, 2]]

    n 頂点 m 辺、必須頂点数 K、復元結果の総頂点数 L とする。
    全頂点必須・点素・始終点自由なら二部マッチングで O((n+m)sqrt(n))。
    その他は O(n+m) 規模のグラフを直接作り、Dinic を高々2回呼ぶ。
    その保守的な時間上界は O((n+1)^2(n+m+1))、空間は O(n+m)。
    始終点自由なら単頂点被覆からの取り消しだけなので最大流1回。
    推移閉包や流量下限付きフローのラッパーは使わない。
    paths は毎回 O(n+m+L) 時間・空間。共有可では L <= nK。
    """

    def __init__(self, n: int, vertex_disjoint: bool = True) -> None:
        assert n >= 0
        self._n = n
        self._disjoint = vertex_disjoint
        self._edges: list[tuple[int, int]] = []
        self._answer = -2
        self._starts: list[int] = []
        self._ends: list[int] = []
        self._edge_flow: list[int] = []

    def add_edge(self, u: int, v: int) -> int:
        """有向辺 u→v を追加し、0 始まりの辺 ID を返す。償却 O(1)。"""
        assert 0 <= u < self._n and 0 <= v < self._n
        edge_id = len(self._edges)
        self._edges.append((u, v))
        self._answer = -2
        return edge_id

    def _check_dag(self) -> None:
        n = self._n
        adj = [[] for _ in range(n)]
        indegree = [0] * n
        for u, v in self._edges:
            adj[u].append(v)
            indegree[v] += 1
        queue = [v for v in range(n) if indegree[v] == 0]
        for u in queue:
            for v in adj[u]:
                indegree[v] -= 1
                if indegree[v] == 0:
                    queue.append(v)
        if len(queue) != n:
            raise ValueError("graph must be a DAG")

    def _solve_matching(self) -> int:
        n = self._n
        matching = BipartiteMatching(n, n)
        for u, v in self._edges:
            matching.add_edge(u, v)
        self._answer = n - matching.solve()
        self._starts = [int(v == -1) for v in matching.mate_right]
        self._ends = [int(v == -1) for v in matching.mate_left]
        self._edge_flow = [0] * len(self._edges)
        for edge_id in matching.matching_edge_ids():
            self._edge_flow[edge_id] = 1
        return self._answer

    def solve(
        self,
        required: list[bool] | None = None,
        start_allowed: list[bool] | None = None,
        end_allowed: list[bool] | None = None,
    ) -> int:
        """最小本数を返す。実行不能は -1。

        各引数は長さ n の bool 配列。None は全要素 True と同じ。
        required は被覆必須、start_allowed/end_allowed は開始/終了の許可。
        毎回再計算し、前回の条件を引き継がない。入力配列は変更・保持しない。
        呼び出し開始時に前回の結果を無効化するため、失敗時も古い復元はできない。
        """
        self._answer = -2
        n = self._n
        if required is None:
            required = [True] * n
        if start_allowed is None:
            start_allowed = [True] * n
        if end_allowed is None:
            end_allowed = [True] * n
        assert len(required) == len(start_allowed) == len(end_allowed) == n
        self._check_dag()
        k = sum(required)
        if k == 0:
            self._answer = 0
            return 0
        free = all(start_allowed) and all(end_allowed)
        if self._disjoint and k == n and free:
            return self._solve_matching()

        s, t = 2 * n, 2 * n + 1
        source, sink = 2 * n + 2, 2 * n + 3
        g = MFGraph(2 * n + (2 if free else 4))
        start_ids = [-1] * n
        end_ids = [-1] * n
        upper = 1 if self._disjoint else k
        for v in range(n):
            r = int(required[v])
            if start_allowed[v]:
                start_ids[v] = g.add_edge(s, v, k)
                if free:
                    g.change_edge(start_ids[v], k, r)
            # 下限 r は暗黙に保持。逆辺で取り消せるのは上乗せ分だけ。
            g.add_edge(v, n + v, upper - r)
            if end_allowed[v]:
                end_ids[v] = g.add_edge(n + v, t, k)
                if free:
                    g.change_edge(end_ids[v], k, r)
        edge_ids = [g.add_edge(n + u, v, k) for u, v in self._edges]

        value = k
        if not free:
            back = g.add_edge(t, s, k)
            auxiliary = []
            for v in range(n):
                if required[v]:
                    auxiliary.append(g.add_edge(source, n + v, 1))
                    auxiliary.append(g.add_edge(v, sink, 1))
            if g.flow(source, sink, k) != k:
                self._answer = -1
                return -1
            value = g.get_edge(back).flow
            for edge_id in auxiliary:
                g.change_edge(edge_id, 0, 0)
            g.change_edge(back, 0, 0)

        self._answer = value - g.flow(t, s, value)
        self._starts = [g.get_edge(i).flow if i != -1 else 0 for i in start_ids]
        self._ends = [g.get_edge(i).flow if i != -1 else 0 for i in end_ids]
        self._edge_flow = [g.get_edge(i).flow for i in edge_ids]
        return self._answer

    def paths(self) -> list[list[int]]:
        """solve 後の頂点列を返す。未計算・実行不能なら RuntimeError。

        内部の結果を変更せず、呼び出すたび独立なリストを返す。
        """
        if self._answer < 0:
            raise RuntimeError("call solve() and check feasibility before paths()")
        if self._answer == 0:
            return []
        n = self._n
        adj = [[] for _ in range(n)]
        for i, (u, v) in enumerate(self._edges):
            if self._edge_flow[i]:
                adj[u].append(i)
        remain = self._edge_flow.copy()
        ends = self._ends.copy()
        current = [0] * n
        result = []
        for start in range(n):
            for _ in range(self._starts[start]):
                v = start
                path = [v]
                while ends[v] == 0:
                    while remain[adj[v][current[v]]] == 0:
                        current[v] += 1
                    i = adj[v][current[v]]
                    remain[i] -= 1
                    v = self._edges[i][1]
                    path.append(v)
                ends[v] -= 1
                result.append(path)
        return result
