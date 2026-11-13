# competitive-verifier: TITLE 頂点容量付き最大本数パス集合（有向・無向）

from python.graph.flow.maxflow.MaxFlow import MFGraph


class VertexCapacitatedPaths:
    """頂点・辺・開始・終了容量の範囲で、単純パスの本数を最大化する。

    一般の有向・無向混在グラフに対応。端点ペアの指定、費用、被覆義務は扱わない。
    各容量は非負整数。同じパスも容量の範囲で複数回選べる。
    vertex_capacity は端点を含む使用本数、start/end_capacity は開始/終了本数。
    開始・終了可能な頂点の途中通過も許す。両方が正なら単頂点パスも許す。
    無向辺は両方向の合計使用本数を制限し、解では逆向き利用を相殺する。

    n 頂点 m 辺を O(n+m) サイズの最大流に帰着。solve は一般に
    O(n^2(n+m)) 時間、O(n+m) 空間。復元は初回 O((n+m)^2)、
    以降は出力サイズに比例。同一パスの重複も paths/edge_paths では展開する。

    使用例（端点以外を共有しない S-T パスを高々 K 本）:
        g = VertexCapacitatedPaths.st(n, S, T, path_limit=K)
        for u, v in edges:
            g.add_undirected_edge(u, v)  # 有向辺なら add_edge
        count = g.solve()
        if count == K:
            paths = g.paths()

    複数終点の例（S から A, B へ各1本、S 以外は共有不可）:
        vc, sc, ec = [1]*n, [0]*n, [0]*n
        vc[S] = sc[S] = 2
        ec[A] = ec[B] = 1
        g = VertexCapacitatedPaths(n, vertex_capacity=vc,
                start_capacity=sc, end_capacity=ec, path_limit=2)
        # 最短路条件があれば、利用側で最短路 DAG の辺だけを追加する。
    """

    def __init__(self, n: int, *, vertex_capacity: list[int],
                 start_capacity: list[int], end_capacity: list[int],
                 path_limit: int | None = None) -> None:
        """容量は長さ n の整数リスト。path_limit=None は本数制限なし。"""
        assert n >= 0
        for caps in (vertex_capacity, start_capacity, end_capacity):
            assert isinstance(caps, list) and len(caps) == n
            assert all(isinstance(c, int) and c >= 0 for c in caps)
        assert path_limit is None or isinstance(path_limit, int) and path_limit >= 0
        self._n = n
        self._vertex = vertex_capacity.copy()
        self._start = start_capacity.copy()
        self._end = end_capacity.copy()
        self._limit = path_limit
        self._s = self._t = -1
        self._edges: list[tuple[int, int, int, bool]] = []
        self._count = -1
        self._parts: list[tuple[int, list[int], list[int]]] = []
        self._restored = False

    @classmethod
    def st(cls, n: int, s: int, t: int, *, path_limit: int | None = None):
        """s,t のみ共有を許す点素パス用。s != t。端点容量は内部で設定する。"""
        assert 0 <= s < n and 0 <= t < n and s != t
        obj = cls(n, vertex_capacity=[1]*n, start_capacity=[0]*n,
                  end_capacity=[0]*n, path_limit=path_limit)
        obj._s, obj._t = s, t
        return obj

    def add_edge(self, u: int, v: int, capacity: int = 1) -> int:
        """有向辺を追加し元の辺 ID を返す。多重辺・自己ループ可。solve 前のみ。"""
        return self._add(u, v, capacity, False)

    def add_undirected_edge(self, u: int, v: int, capacity: int = 1) -> int:
        """両方向合計の容量を持つ無向辺を追加し、方向共通の辺 ID を返す。"""
        return self._add(u, v, capacity, True)

    def _add(self, u, v, capacity, undirected):
        if self._count >= 0:
            raise RuntimeError("call add_edge() before solve()")
        assert 0 <= u < self._n and 0 <= v < self._n
        assert isinstance(capacity, int) and capacity >= 0
        i = len(self._edges)
        self._edges.append((u, v, capacity, undirected))
        return i

    def solve(self) -> int:
        """上限までの最大本数を返す。1回限定。ちょうど K 本の判定は返り値 == K。"""
        if self._count >= 0:
            raise RuntimeError("solve() can only be called once")
        n = self._n
        vc, sc, ec = self._vertex.copy(), self._start.copy(), self._end.copy()
        if self._s >= 0:
            bound = sum(c for _, _, c, _ in self._edges)
            if self._limit is not None:
                bound = min(bound, self._limit)
            vc[self._s] = vc[self._t] = bound
            sc[self._s] = ec[self._t] = bound
        source, sink = 2*n, 2*n+1
        g = MFGraph(2*n+2)
        vertex_ids = [g.add_edge(2*v, 2*v+1, vc[v]) for v in range(n)]
        mapping = [-1] * n
        for v in range(n):
            if sc[v]:
                g.add_edge(source, 2*v, sc[v])
                mapping.append(-1)
            if ec[v]:
                g.add_edge(2*v+1, sink, ec[v])
                mapping.append(-1)
        pairs = []
        for i, (u, v, c, undirected) in enumerate(self._edges):
            a = g.add_edge(2*u+1, 2*v, c)
            mapping.append(i)
            if undirected:
                b = g.add_edge(2*v+1, 2*u, c)
                mapping.append(i)
                pairs.append((u, v, a, b))
        self._count = g.flow(source, sink, self._limit)
        # u_out -> v_in -> v_out -> u_in -> u_out の循環を除く。
        for u, v, a, b in pairs:
            ea, eb = g.get_edge(a), g.get_edge(b)
            delta = min(ea.flow, eb.flow)
            if delta:
                g.change_edge(a, ea.cap, ea.flow-delta)
                g.change_edge(b, eb.cap, eb.flow-delta)
                for w in (u, v):
                    e = g.get_edge(vertex_ids[w])
                    g.change_edge(vertex_ids[w], e.cap, e.flow-delta)
        self._graph = g
        self._mapping = mapping
        return self._count

    def _restore(self):
        if self._count < 0:
            raise RuntimeError("call solve() before paths()")
        if self._restored:
            return
        g = self._graph
        for f, ids in g.path_decomposition(2*self._n, 2*self._n+1):
            vertices = [g.get_edge(ids[0]).dst // 2]
            original_ids = []
            for i in ids:
                if self._mapping[i] >= 0:
                    original_ids.append(self._mapping[i])
                    vertices.append(g.get_edge(i).dst // 2)
            self._parts.append((f, vertices, original_ids))
        self._restored = True

    def paths(self) -> list[list[int]]:
        """解の頂点列。各パスは単純。独立なリストを返し、内部状態を変更しない。"""
        self._restore()
        return [vs.copy() for f, vs, _ in self._parts for _ in range(f)]

    def edge_paths(self) -> list[list[int]]:
        """paths と同順の元の辺 ID 列。無向辺の向きは対応する頂点列から分かる。"""
        self._restore()
        return [es.copy() for f, _, es in self._parts for _ in range(f)]
