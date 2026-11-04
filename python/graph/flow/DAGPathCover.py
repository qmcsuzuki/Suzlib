# competitive-verifier: TITLE DAG の最小費用パス被覆・パス選択

from python.graph.flow.MinCostFlow import DAGMCFGraph


class DAGPathCover:
    """DAG のパス集合について、開始費用 + 終了費用 + 辺費用 - 頂点報酬を最小化。

    デフォルトは全頂点必須・点素・開始費用1なので、最小本数のパス被覆。
    条件はコンストラクタで確定し、辺を追加して solve() を一度だけ呼ぶ。
    成功時は (本数, 総費用)、実行不能は (-1, 0)。同費用なら本数最小。
    頂点番号は任意の 0..n-1。単頂点パス、多重辺、空グラフを許す。
    共有可では同じパスを複数回選べる。空パスは結果に含めない。

    使用例:
        g = DAGPathCover(3)
        g.add_edge(0, 1)
        g.add_edge(1, 2)
        count, cost = g.solve()  # (1, 1)
        paths = g.paths()       # [[0, 1, 2]]

        # PAST202107 M 型: start_cost=C、辺費用 abs(A[j]-A[i])。
        # TDPC R 型（SCC 縮約は呼び出し側）:
        g = DAGPathCover(3, vertex_disjoint=False, required=False,
                         path_limit=2, start_cost=0, vertex_gain=[1, 1, 1])
        g.add_edge(0, 2)
        g.add_edge(1, 2)
        count, cost = g.solve()  # (2, -3)。最大報酬は -cost。

    全ケースで DAGMCFGraph を使う。必須頂点の分割辺の下限1を収支へ移し、
    未使用の本数枠を s→t のダミー辺に流すことで DAG のまま固定流量に帰着。
    整数費用を (K+1) 倍し、開始辺に1を足して本数を第二目的とする。
    二部マッチング、最大流、b-flow クラス、必須頂点への罰金は使わない。

    n 頂点 m 辺、実効本数上限 K、必須頂点数 R、最短路反復回数 A として
    A <= K+R。構築 O(n+m)、空間 O(n+m)。solve の時間は sparse で
    O(n+m + A*(n+m+1)*log(n+m+2))、dense で O(n+m + A*((n+1)**2+m))。
    復元は総出力頂点数 L <= nK に対し O(n+m+L) 時間・空間。
    旧 DAGPathCover の solve 引数・整数返却と DAGPathOptimization は廃止。
    """

    def __init__(
        self, n: int, vertex_disjoint: bool = True, *,
        required: bool | list[bool] | None = None,
        path_count: int | None = None,
        path_limit: int | None = None,
        start_cost: int | list[int] = 1,
        end_cost: int | list[int] = 0,
        vertex_gain: int | list[int] = 0,
        gain_once: bool = True,
        start_allowed: list[bool] | None = None,
        end_allowed: list[bool] | None = None,
        dense: bool = False,
    ) -> None:
        """条件をコピーして保持する。費用・報酬は整数または長さnの整数配列。

        required=None/True は全頂点必須、False は義務なし、配列は頂点ごと。
        path_count はちょうど、path_limit は高々の本数。併用不可。
        本数指定なしは点素なら上限n。共有可では gain_once=True かつ
        開始・終了・辺費用がすべて非負の場合のみ上限nとし、それ以外は指定必須。
        共有可かつ gain_once=True では頂点報酬は非負に限る。
        点素または gain_once=False なら負の頂点報酬も許す。
        始終点許可は長さnのbool配列。None は全頂点許可。
        """
        assert n >= 0
        if path_count is not None and path_limit is not None:
            raise ValueError("path_count and path_limit are mutually exclusive")
        if path_count is not None:
            assert path_count >= 0
        if path_limit is not None:
            assert path_limit >= 0

        def values(value):
            if isinstance(value, int):
                return [value] * n
            assert len(value) == n
            return list(value)

        self._n = n
        self._disjoint = vertex_disjoint
        self._required = values(True if required is None else required)
        self._start_cost = values(start_cost)
        self._end_cost = values(end_cost)
        self._gain = values(vertex_gain)
        self._start_allowed = values(True if start_allowed is None else start_allowed)
        self._end_allowed = values(True if end_allowed is None else end_allowed)
        self._once = gain_once
        self._exact = path_count
        self._limit = path_limit
        self._dense = dense
        if not vertex_disjoint and gain_once and any(w < 0 for w in self._gain):
            raise ValueError("shared first-visit gains must be nonnegative")
        self._edges: list[tuple[int, int, int]] = []
        self._used = False
        self._count = -1
        self._starts: list[int] = []
        self._ends: list[int] = []
        self._edge_flow: list[int] = []

    def add_edge(self, u: int, v: int, cost: int = 0) -> int:
        """費用costの辺を追加してIDを返す。負費用も可。solve前のみ。償却O(1)。"""
        if self._used:
            raise RuntimeError("call add_edge() before solve()")
        assert 0 <= u < self._n and 0 <= v < self._n
        i = len(self._edges)
        self._edges.append((u, v, cost))
        return i

    def solve(self) -> tuple[int, int]:
        """(本数, 最小総費用) を返す。実行不能は (-1, 0)。一度だけ呼べる。

        閉路（自己ループ含む）や共有可で必要な本数指定がない場合は ValueError。
        """
        if self._used:
            raise RuntimeError("solve() can only be called once")
        self._used = True
        n = self._n
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

        k = self._exact if self._exact is not None else self._limit
        if k is None:
            if not self._disjoint and (
                not self._once or any(c < 0 for c in self._start_cost)
                or any(c < 0 for c in self._end_cost)
                or any(c < 0 for _, _, c in self._edges)
            ):
                raise ValueError("specify path_count or path_limit for this shared-path problem")
            k = n
        if self._disjoint:
            if self._exact is not None and k > n:
                return -1, 0
            k = min(k, n)
        if k == 0:
            if any(self._required):
                return -1, 0
            self._count = 0
            return 0, 0

        # 順序は source, s, 各頂点のin/out, t, sink。
        s, t = 0, 2 * n + 1
        source, sink = t + 1, t + 2
        g = DAGMCFGraph(t + 3, source, sink, dense=self._dense)
        rank = [0] * n
        for i, v in enumerate(order):
            rank[v] = 2 * i + 1
        balance = [0] * (t + 1)
        balance[s], balance[t] = k, -k
        scale = k + 1
        base_cost = 0
        starts = [-1] * n
        ends = [-1] * n
        for v in range(n):
            vin = rank[v]
            r = int(bool(self._required[v]))
            reward = self._gain[v] * scale
            if self._start_allowed[v]:
                starts[v] = g.add_edge(s, vin, k, self._start_cost[v] * scale + 1)
            if self._end_allowed[v]:
                ends[v] = g.add_edge(vin + 1, t, k, self._end_cost[v] * scale)
            # 初回辺（または通過辺）の下限rを引く。固定費用も保存。
            upper = 1 if self._disjoint or self._once else k
            g.add_edge(vin, vin + 1, upper - r, -reward)
            if not self._disjoint and self._once and k > 1:
                g.add_edge(vin, vin + 1, k - 1, 0)
            balance[vin] -= r
            balance[vin + 1] += r
            base_cost -= r * reward
        edge_ids = [g.add_edge(rank[u] + 1, rank[v], k, c * scale)
                    for u, v, c in self._edges]
        if self._exact is None:
            g.add_edge(s, t, k, 0)  # 使わない本数枠。
        demand = 0
        for v, b in enumerate(balance):
            if b > 0:
                g.add_edge(source, v, b, 0)
                demand += b
            elif b < 0:
                g.add_edge(v, sink, -b, 0)
        flow, cost = g.flow(demand)
        if flow != demand:
            return -1, 0
        self._starts = [g.get_edge(i).flow if i >= 0 else 0 for i in starts]
        self._ends = [g.get_edge(i).flow if i >= 0 else 0 for i in ends]
        self._edge_flow = [g.get_edge(i).flow for i in edge_ids]
        self._count = sum(self._starts)
        return self._count, (base_cost + cost - self._count) // scale

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
