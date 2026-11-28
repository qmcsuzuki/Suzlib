# competitive-verifier: TITLE 最大流による DAG の最小パス被覆・最大重み反鎖

from python.graph.flow.maxflow.MaxFlow import MFGraph
from python.graph.topological_sort import topological_sort


def _minimum_cover_flow(n, edges, lower, disjoint):
    """各頂点の被覆回数の下限を満たす最小本数と、求解済みのグラフ・辺番号を返す。
    初期解（各 v を lower[v] 本の単頂点パスで覆う解）から流を押し戻すアルゴリズム
    """
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    if topological_sort(adj) is None:
        raise ValueError("graph must be a DAG")
    s, t = 2 * n, 2 * n + 1
    total = sum(lower)
    big = total + 1
    g = MFGraph(2 * n + 2)
    start = []
    for v, w in enumerate(lower):
        g.add_edge(s, v, w)
        start.append(g.add_edge(n + v, t, w))
        g.add_edge(n + v, v, (1 if disjoint else big) - w)
    edge_ids = [g.add_edge(u, n + v, big) for u, v in edges]
    return total - g.flow(s, t), g, start, edge_ids


class DAGMinimumPathCover:
    """DAG の各頂点を指定回数以上覆う最小本数のパス被覆とパス列。
    weights=None は各頂点1回。disjoint=True で点素、False で頂点共有可。
    点素の場合は weights の各要素を0または1に制限する。単頂点パスも許す。
    solve は 2n+2 頂点・3n+m 辺の最大流を 1 回。復元は O(n+m+出力長)。

    注！！！ 推移閉包となる辺が与えられる場合は、マッチング版の方が高速 ！！！
    """

    def __init__(
        self, n: int, *, disjoint: bool = True, weights: list[int] | None = None
    ) -> None:
        """weights[v] 回以上頂点 v を被覆する。None は全頂点1回。"""
        assert n >= 0
        if weights is not None:
            assert len(weights) == n and all(isinstance(w, int) and w >= 0 for w in weights)
            if disjoint and any(w > 1 for w in weights):
                raise ValueError("disjoint path cover cannot require more than one visit")
        self._weights = [1] * n if weights is None else list(weights)
        self._n = n
        self._disjoint = disjoint
        self._edges = []
        self._used = False
        self._flow = None

    def add_edge(self, u: int, v: int) -> int:
        """solve 前に辺 u→v を追加し、0 始まりの辺番号を返す。"""
        if self._used:
            raise RuntimeError("call add_edge() before solve()")
        assert 0 <= u < self._n and 0 <= v < self._n
        self._edges.append((u, v))
        return len(self._edges) - 1

    def solve(self) -> int:
        """各頂点の必要被覆回数を満たす最小本数を返す。呼び出しは1回限り。"""
        if self._used:
            raise RuntimeError("solve() can only be called once")
        self._used = True
        count, self._flow, self._start_ids, self._edge_ids = _minimum_cover_flow(
            self._n, self._edges, self._weights, self._disjoint)
        return count

    def _paths(self, edge_ids):
        """求解済みのフローから各パスを復元し、edge_ids に応じて辺番号列または頂点列で返す。"""
        if self._flow is None:
            raise RuntimeError("call solve() before paths()")
        n = self._n
        outgoing = [[] for _ in range(n)]
        remaining = []
        for i, (u, v) in enumerate(self._edges):
            amount = self._flow.get_edge(self._edge_ids[i]).flow
            remaining.append(amount)
            if amount:
                outgoing[u].append(i)
        paths = []
        for start in range(n):
            # start から始まるパスは、他のパスへつながれずに残った n+start→t の容量。
            e = self._flow.get_edge(self._start_ids[start])
            for _ in range(e.cap - e.flow):
                u = start
                path = [] if edge_ids else [u]
                while outgoing[u]:
                    i = outgoing[u][-1]
                    remaining[i] -= 1
                    if not remaining[i]:
                        outgoing[u].pop()
                    u = self._edges[i][1]
                    path.append(i if edge_ids else u)
                paths.append(path)
        return paths

    def paths(self) -> list[list[int]]:
        """solve 後、最小パス被覆の各パスを頂点列で返す。"""
        return self._paths(False)

    def edge_paths(self) -> list[list[int]]:
        """solve 後、最小パス被覆の各パスを辺番号列で返す。単頂点パスは空リストになる。"""
        return self._paths(True)


class DAGMaximumAntichain(DAGMinimumPathCover):
    """solve() で最大重みを求め、antichain() で反鎖、paths() で対応するパス被覆を復元する。"""

    def __init__(self, n: int, weights: list[int] | None = None) -> None:
        super().__init__(n, disjoint=False, weights=weights)

    def antichain(self) -> list[int]:
        """solve 後、最大重みを達成する反鎖の頂点列を復元する。"""
        if self._flow is None:
            raise RuntimeError("call solve() before antichain()")
        # 最小カットで s 側の v と t 側の n+v の組が反鎖をなす。u→n+v と n+v→v の
        # 容量は十分大きいので、u が s 側なら u から到達可能な頂点 v の n+v も s 側になる。
        n = self._n
        side = self._flow.min_cut(2 * n)
        return [v for v in range(n) if side[v] and not side[n + v]]
