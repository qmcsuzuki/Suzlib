# competitive-verifier: TITLE DAG の最小本数パス被覆

from python.graph.flow.LowerBoundSTFlow import LowerBoundSTFlow
from python.graph.matching.BipartiteMatching import BipartiteMatching


class DAGMinimumPathCover:
    """必須頂点を被覆する非空パスの最小本数。費用は扱わない。

    vertex_disjoint=True は点素、False は頂点・辺の共有可。
    required=None は全頂点必須、配列では True の頂点だけ必須。
    start_capacity/end_capacity は頂点ごとの開始/終了本数上限。
    None は個別制限なし、指定時は長さ n の非負整数リスト。
    単頂点パスを許し、共有可では同じパスを複数回選べる。
    入力は DAG に限る。頂点番号のトポロジカル順は不要。

    点素・全頂点必須・全頂点で開始終了可能なら二部最大マッチング。
    それ以外は頂点分割し、必須頂点の通過量に下限1を設定して
    LowerBoundSTFlow で総流量を最小化する（最大流を高々2回）。
    n 頂点 m 辺に対し、基本形 O((n+m) sqrt(n))、一般形 O(n^2(n+m))、
    空間 O(n+m)。復元は O(n+m+出力長)。

    使用例（n: 頂点数、edges: 有向辺 (u, v) の列）:
        # 点素パス被覆（全頂点を被覆し、本数最小）
        g = DAGMinimumPathCover(n, vertex_disjoint=True)
        # 頂点共有可で全頂点を被覆
        g = DAGMinimumPathCover(n, vertex_disjoint=False)
        # 指定頂点だけ必須、各始点を高々1回使用（required: 長さnのbool配列）
        g = DAGMinimumPathCover(n, vertex_disjoint=False, required=required, start_capacity=[1]*n)

        # 上のいずれかで初期化後
        for u, v in edges:
            g.add_edge(u, v)
        count = g.solve()  # 最小本数。実行不能なら -1
        if count != -1:
            paths = g.paths()  # 各パスの頂点列
    """

    def __init__(self, n: int, vertex_disjoint: bool = True, *,
                 required: list[bool] | None = None,
                 start_capacity: list[int] | None = None,
                 end_capacity: list[int] | None = None) -> None:
        """条件を固定する。配列はコピーして保持する。O(n)。"""
        assert n >= 0
        if required is not None:
            assert isinstance(required, list) and len(required) == n
            assert all(isinstance(r, bool) for r in required)
        for caps in (start_capacity, end_capacity):
            if caps is not None:
                assert isinstance(caps, list) and len(caps) == n
                assert all(isinstance(c, int) and c >= 0 for c in caps)
        self._n = n
        self._disjoint = vertex_disjoint
        self._required = [True] * n if required is None else required.copy()
        self._start_capacity = [n] * n if start_capacity is None else start_capacity.copy()
        self._end_capacity = [n] * n if end_capacity is None else end_capacity.copy()
        self._edges: list[tuple[int, int]] = []
        self._used = False
        self._count = -1
        self._starts: list[int] = []
        self._ends: list[int] = []
        self._edge_flow: list[int] = []

    def add_edge(self, u: int, v: int) -> int:
        """有向辺を追加し辺IDを返す。多重辺可、solve 前のみ。償却 O(1)。"""
        if self._used:
            raise RuntimeError("call add_edge() before solve()")
        assert 0 <= u < self._n and 0 <= v < self._n
        i = len(self._edges)
        self._edges.append((u, v))
        return i

    def solve(self) -> int:
        """最小本数を返す。実行不能は -1、DAG でなければ ValueError。1回限定。"""
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
        if not any(self._required):
            self._starts = [0] * n
            self._ends = [0] * n
            self._edge_flow = [0] * len(self._edges)
            self._count = 0
            return 0
        if (self._disjoint and all(self._required)
                and all(self._start_capacity) and all(self._end_capacity)):
            g = BipartiteMatching(n, n)
            for u, v in self._edges:
                g.add_edge(u, v)
            self._count = n - g.solve()
            self._starts = [1] * n
            self._ends = [1] * n
            self._edge_flow = [0] * len(self._edges)
            for i in g.matching_edge_ids():
                u, v = self._edges[i]
                self._starts[v] = 0
                self._ends[u] = 0
                self._edge_flow[i] = 1
            return self._count

        # 最小解の各パスは固有の必須頂点を持つ。なければそのパスを除ける。
        # よって必須頂点数 R を、全ての容量と総流量の安全な上限にできる。
        limit = sum(self._required)
        s, t = 2 * n, 2 * n + 1
        g = LowerBoundSTFlow(t + 1, s, t)
        starts = []
        ends = []
        for v in range(n):
            starts.append(g.add_edge(s, 2 * v, 0, min(limit, self._start_capacity[v])))
            g.add_edge(2 * v, 2 * v + 1, int(self._required[v]),
                       1 if self._disjoint else limit)
            ends.append(g.add_edge(2 * v + 1, t, 0, min(limit, self._end_capacity[v])))
        edge_ids = [g.add_edge(2 * u + 1, 2 * v, 0, limit) for u, v in self._edges]
        if not g.solve(flow_upper=limit):
            return -1
        self._count = g.minimize()
        self._starts = [g.get_edge(i).flow for i in starts]
        self._ends = [g.get_edge(i).flow for i in ends]
        self._edge_flow = [g.get_edge(i).flow for i in edge_ids]
        return self._count

    def paths(self) -> list[list[int]]:
        """解の頂点列を独立なリストで返す。未計算・失敗後は RuntimeError。"""
        return self._paths(False)

    def edge_paths(self) -> list[list[int]]:
        """paths と同順の辺ID列。単頂点パスは空列。内部状態は変更しない。"""
        return self._paths(True)

    def _paths(self, edge_ids: bool) -> list[list[int]]:
        if self._count < 0:
            raise RuntimeError("call solve() and check feasibility before paths()")
        adj = [[] for _ in range(self._n)]
        for i, (u, _) in enumerate(self._edges):
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
