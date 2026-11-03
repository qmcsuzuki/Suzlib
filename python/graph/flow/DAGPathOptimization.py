# competitive-verifier: TITLE DAG 上の複数パスの最大利得

from python.graph.flow.MinCostFlow import DAGMCFGraph


class DAGPathOptimization:
    """DAG 上でパスを選び、頂点報酬 - 辺の通過費用を最大化する。

    頂点番号は 0..n-1。内部でトポロジカルソートするため番号順は任意。
    SCC 縮約は呼び出し側で行う。単頂点パス・多重辺・空グラフを許す。
    共有可では同一パスを複数回選べる。空パスは選ばない。
    solve は毎回再構築し、paths は直近の成功した計算の頂点列を返す。

    使用例（SCC 縮約後、2 本で訪れる頂点の重みの和を最大化）:
        g = DAGPathOptimization(3)
        g.add_edge(0, 2)
        g.add_edge(1, 2)
        count, gain = g.solve(2, vertex_gain=[1, 1, 1])  # (2, 3)
        paths = g.paths()  # [[0, 2], [1, 2]] など

    n 頂点 m 辺、最短路反復回数 A <= K として、構築 O(n+m)、
    sparse の計算は O(n+m + A*(n+m)*log(n+m+2))、
    dense=True は O(n+m + A*(n*n+m))。空間 O(n+m)。
    復元は総出力頂点数 L に対して O(n+m+L) 時間・空間。L <= nK。
    """

    def __init__(self, n: int, dense: bool = False) -> None:
        assert n >= 0
        self._n = n
        self._dense = dense
        self._edges: list[tuple[int, int, int]] = []
        self._count = -1
        self._starts: list[int] = []
        self._ends: list[int] = []
        self._edge_flow: list[int] = []

    def add_edge(self, u: int, v: int, cost: int = 0) -> int:
        """辺を追加して ID を返す。費用は通過ごとに発生し、負でもよい。O(1)。"""
        assert 0 <= u < self._n and 0 <= v < self._n
        i = len(self._edges)
        self._edges.append((u, v, cost))
        self._count = -1
        return i

    def solve(
        self,
        K: int,
        vertex_gain: list[int] | None = None,
        vertex_disjoint: bool = False,
        gain_once: bool = True,
        exact: bool = False,
        start_allowed: list[bool] | None = None,
        end_allowed: list[bool] | None = None,
    ) -> tuple[int, int]:
        """(本数, 最大利得) を返す。exact=True で実行不能なら (-1, 0)。

        K は非負。exact=False は高々 K 本、True はちょうど K 本。
        高々 K 本の場合は同利得なら本数最小（0 本も可）。
        vertex_gain は長さ n の整数配列、None は全要素 0。
        gain_once=True は訪れた頂点の報酬を一度だけ、False は通過ごとに加算。
        共有可かつ gain_once=True では報酬は非負に限る。
        点素または gain_once=False なら負の報酬も許す。
        start_allowed/end_allowed は長さ n の bool 配列、None は全要素 True。
        入力配列は変更・保持しない。条件は呼び出しごとに指定する。
        閉路・自己ループは ValueError。失敗時は以前の復元結果も無効。
        純粋な最小費用問題は報酬を 0 にし、返る利得の符号を反転する。
        """
        self._count = -1
        assert K >= 0
        n = self._n
        if vertex_gain is None:
            vertex_gain = [0] * n
        if start_allowed is None:
            start_allowed = [True] * n
        if end_allowed is None:
            end_allowed = [True] * n
        assert len(vertex_gain) == len(start_allowed) == len(end_allowed) == n
        if gain_once and not vertex_disjoint and any(w < 0 for w in vertex_gain):
            raise ValueError("shared first-visit gains must be nonnegative")

        adj = [[] for _ in range(n)]
        indegree = [0] * n
        for u, v, _ in self._edges:
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
        if K == 0:
            self._count = 0
            return 0, 0

        rank = [0] * n
        for i, v in enumerate(order):
            rank[v] = 2 * i
        s, t = 2 * n, 2 * n + 1
        g = DAGMCFGraph(2 * n + 2, s, t, dense=self._dense)
        starts = [-1] * n
        ends = [-1] * n
        for v in range(n):
            vin = rank[v]
            if start_allowed[v]:
                starts[v] = g.add_edge(s, vin, K, 0)
            if end_allowed[v]:
                ends[v] = g.add_edge(vin + 1, t, K, 0)
            if vertex_disjoint:
                g.add_edge(vin, vin + 1, 1, -vertex_gain[v])
            elif gain_once:
                g.add_edge(vin, vin + 1, 1, -vertex_gain[v])
                if K > 1:
                    g.add_edge(vin, vin + 1, K - 1, 0)
            else:
                g.add_edge(vin, vin + 1, K, -vertex_gain[v])
        edges = [g.add_edge(rank[u] + 1, rank[v], K, cost)
                 for u, v, cost in self._edges]
        count, cost = g.flow(K) if exact else g.min_cost_flow(K)
        if exact and count != K:
            return -1, 0
        self._starts = [g.get_edge(i).flow if i != -1 else 0 for i in starts]
        self._ends = [g.get_edge(i).flow if i != -1 else 0 for i in ends]
        self._edge_flow = [g.get_edge(i).flow for i in edges]
        self._count = count
        return count, -cost

    def paths(self) -> list[list[int]]:
        """直近の解の頂点列を独立なリストで返す。未計算・失敗後は RuntimeError。

        内部状態を変更しない。多重辺の区別が必要な場合は edge_paths を用いる。
        """
        return self._paths(False)

    def edge_paths(self) -> list[list[int]]:
        """直近の解の辺 ID 列を返す。順序は paths と対応し、単頂点パスは空列。"""
        return self._paths(True)

    def _paths(self, edge_ids: bool) -> list[list[int]]:
        if self._count < 0:
            raise RuntimeError("call solve() and check feasibility before paths()")
        if self._count == 0:
            return []
        adj = [[] for _ in range(self._n)]
        for i, (u, _, _) in enumerate(self._edges):
            if self._edge_flow[i]:
                adj[u].append(i)
        remain = self._edge_flow.copy()
        ends = self._ends.copy()
        current = [0] * self._n
        result = []
        for start, count in enumerate(self._starts):
            for _ in range(count):
                v = start
                path = [] if edge_ids else [v]
                while ends[v] == 0:
                    while remain[adj[v][current[v]]] == 0:
                        current[v] += 1
                    i = adj[v][current[v]]
                    remain[i] -= 1
                    v = self._edges[i][1]
                    path.append(i if edge_ids else v)
                ends[v] -= 1
                result.append(path)
        return result
