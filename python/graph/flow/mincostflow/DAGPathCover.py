# competitive-verifier: TITLE DAG の最小費用パス被覆・パス選択

from python.graph.flow.mincostflow.DAGLowerBoundMinCostFlow import DAGLowerBoundMinCostFlow


class DAGPathCover:
    """DAG のパス集合について、開始費用 + 終了費用 + 辺費用 - 頂点報酬を最小化。
    成功時は (本数, 総費用)、実行不能は (-1, 0)。同費用なら本数最小。共有可では同じパスを複数回選べる。空パスは結果に含めない。

    使用例（n: 頂点数、K: 本数、weights: 各頂点の報酬）:
        # 点素パス被覆（全頂点を被覆し、本数最小。辺費用は0）
        DAGPathCover(n, vertex_disjoint=True, required=True, path_count=None, path_limit=None, start_cost=1, end_cost=0, vertex_gain=0, gain_once=True)
        # K本・頂点報酬は1回のみ（頂点共有可、被覆義務なし）
        DAGPathCover(n, vertex_disjoint=False, required=False, path_count=K, path_limit=None, start_cost=0, end_cost=0, vertex_gain=weights, gain_once=True)

    最適化には DAGLowerBoundMinCostFlow を使い、ネットワークは常に DAG のまま。
    - 点素・全頂点必須・全頂点で開始終了可能: 二部マッチングに帰着する。
      初期状態は全頂点が単独パス。辺 u→v の結合費用は c_uv-C_u-B_v。
      本数ちょうど K は n-K 個のマッチ、本数高々 K は n 単位の流量と
      容量 K の s→t 直通辺で表す。
    - その他: 頂点を in/out に分割し、必須頂点の in→out 辺に下限1を付けた
      s-t 流。本数ちょうど K は solve(K)、高々 K は min_cost_flow(K)。

    同費用なら本数最小とするための費用拡大は、上限 K に依存しない。
    - 分割グラフ: 本数 = s-t 流量なので、DAGLowerBoundMinCostFlow.min_cost_flow
      の「同費用なら流量最小」をそのまま使う（内部の倍率は2）。
    - 二部マッチングの本数高々 K: 本数 = 直通辺の流量。結合費用を2倍し直通辺を
      費用1にする。単純閉路は直通辺を高々1回通るので、実費用が負の閉路は負の
      まま残り、実費用0で本数を減らす閉路だけが負になる。
    - 本数ちょうど K では本数が固定なので拡大しない。

    n 頂点 m 辺、実効本数上限 K、必須頂点数 R、増流回数上界 A として
    必須なしは A<=K、点素全被覆は A<=n、一般の場合は A<=K+R。
    """

    def __init__(
        self, n: int, vertex_disjoint: bool, *,
        required: bool | list[bool] | None,
        path_count: int | None,
        path_limit: int | None,
        start_cost: int | list[int],
        end_cost: int | list[int],
        vertex_gain: int | list[int],
        gain_once: bool,
        start_capacity: list[int] | None = None,
        end_capacity: list[int] | None = None,
        dense: bool = False,
    ) -> None:
        """費用・報酬は整数または長さnの整数配列。

        required=None/True は全頂点必須、False は義務なし、配列は頂点ごと。
        path_count はちょうど、path_limit は高々の本数。両方を明示し、
        使用しない側には None を渡す。両方に整数を指定することは不可。
        両方 None は点素なら上限n。共有可では gain_once=True かつ
        開始・終了・辺費用がすべて非負の場合のみ上限nとし、それ以外は指定必須。
        共有可かつ gain_once=True では頂点報酬は非負に限る。
        点素または gain_once=False なら負の頂点報酬も許す。
        start_capacity / end_capacity は各頂点で開始 / 終了できるパス数の上限。
        指定する場合は長さnの非負整数配列。要素 i が頂点 i の上限を表す。
        None は個別の制限なし。途中の頂点共有は vertex_disjoint で指定する。
        例: start_capacity=[1]*n, end_capacity=None は各始点を高々1回、終点は制限なし。
        旧 start_allowed / end_allowed は廃止。許可は本数上限K、禁止は0へ置換する。
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
        # -1 は個別制限なしの内部表現。入力の負容量は許さない。
        if start_capacity is not None:
            assert isinstance(start_capacity, list) and len(start_capacity) == n
            assert all(isinstance(c, int) and c >= 0 for c in start_capacity)
        if end_capacity is not None:
            assert isinstance(end_capacity, list) and len(end_capacity) == n
            assert all(isinstance(c, int) and c >= 0 for c in end_capacity)
        self._start_capacity = [-1] * n if start_capacity is None else start_capacity.copy()
        self._end_capacity = [-1] * n if end_capacity is None else end_capacity.copy()
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
        """(本数, 最小総費用) を返す。実行不能は (-1, 0)。一度だけ呼べる。"""
        if self._used:
            raise RuntimeError("solve() can only be called once")
        self._used = True
        n = self._n

        k = self._exact if self._exact is not None else self._limit
        if k is None:
            if not self._disjoint and (
                not self._once or any(c < 0 for c in self._start_cost)
                or any(c < 0 for c in self._end_cost)
                or any(c < 0 for _, _, c in self._edges)
            ):
                raise ValueError("specify path_count or path_limit for this shared-path problem")
            k = n
        if self._disjoint and self._exact is None:
            k = min(k, n)
        if (self._disjoint and all(self._required)
                and all(self._start_capacity) and all(self._end_capacity)
                and k <= n):
            return self._solve_full_cover(k)
        return self._solve_lower_bound(k)

    def _store(self, starts: list[int], ends: list[int],
               edge_flow: list[int], cost: int) -> tuple[int, int]:
        """各帰着で共通の復元用情報を保存する。"""
        self._starts = starts
        self._ends = ends
        self._edge_flow = edge_flow
        self._count = sum(starts)
        return self._count, cost

    def _solve_lower_bound(self, k: int) -> tuple[int, int]:
        """頂点を in/out に分割し、必須頂点を下限1とする DAG 上の s-t 流。"""
        n = self._n
        s, t = 0, 2 * n + 1
        g = DAGLowerBoundMinCostFlow(t + 1, s, t, dense=self._dense)
        starts = [-1] * n
        ends = [-1] * n
        for v in range(n):
            vin = 2 * v + 1
            start_cap = self._start_capacity[v]
            end_cap = self._end_capacity[v]
            if start_cap:
                cap = k if start_cap < 0 else min(k, start_cap)
                starts[v] = g.add_edge(s, vin, 0, cap, self._start_cost[v])
            if end_cap:
                cap = k if end_cap < 0 else min(k, end_cap)
                ends[v] = g.add_edge(vin + 1, t, 0, cap, self._end_cost[v])
            r = 1 if self._required[v] else 0
            upper = 1 if self._disjoint or self._once else k
            g.add_edge(vin, vin + 1, r, max(upper, r), -self._gain[v])
            if not self._disjoint and self._once and k > 1:
                g.add_edge(vin, vin + 1, 0, k - 1, 0)
        edge_ids = [g.add_edge(2 * u + 2, 2 * v + 1, 0, k, c)
                    for u, v, c in self._edges]
        if self._exact is None:
            count, cost = g.min_cost_flow(k)
        else:
            count, cost = g.solve(k)
        if count < 0:
            return -1, 0
        start_flow = [g.get_edge(i).flow if i >= 0 else 0 for i in starts]
        end_flow = [g.get_edge(i).flow if i >= 0 else 0 for i in ends]
        edge_flow = [g.get_edge(i).flow for i in edge_ids]
        return self._store(start_flow, end_flow, edge_flow, cost)

    def _solve_full_cover(self, k: int) -> tuple[int, int]:
        """点素全被覆、全頂点で開始終了可能。単頂点パスから結合する二部 MCF。"""
        n = self._n
        indegree = [0] * n
        adj = [[] for _ in range(n)]
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
        s, t = 0, 2 * n + 1
        g = DAGLowerBoundMinCostFlow(t + 1, s, t, dense=self._dense)
        join = [c - self._end_cost[u] - self._start_cost[v] for u, v, c in self._edges]
        if self._exact is None:
            # n 単位を、マッチング辺か高々 k 単位の直通辺で流す。
            # 結合費用を2倍し直通辺を費用1にすると、同費用ならマッチ数最大。
            edge_ids = [g.add_edge(u + 1, n + v + 1, 0, 1, 2 * c)
                        for (u, v, _), c in zip(self._edges, join)]
            g.add_edge(s, t, 0, k, 1)
            demand = n
        else:
            edge_ids = [g.add_edge(u + 1, n + v + 1, 0, 1, c)
                        for (u, v, _), c in zip(self._edges, join)]
            demand = n - k
        for v in range(n):
            g.add_edge(s, v + 1, 0, 1, 0)
            g.add_edge(n + v + 1, t, 0, 1, 0)
        if g.solve(demand)[0] < 0:
            return -1, 0
        edge_flow = [g.get_edge(i).flow for i in edge_ids]
        starts = [1] * n
        ends = [1] * n
        for (u, v, _), f in zip(self._edges, edge_flow):
            starts[v] -= f
            ends[u] -= f
        base = sum(self._start_cost) + sum(self._end_cost) - sum(self._gain)
        return self._store(starts, ends, edge_flow,
                           base + sum(f * c for f, c in zip(edge_flow, join)))

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
