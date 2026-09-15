# competitive-verifier: TITLE 二部マッチングの構造

"""
DM分解、マッチングに使う辺・頂点
"""

from python.graph.BipartiteMatching import BipartiteMatching, GeneralBipartiteMatching
from python.graph.SCC import find_SCC


REMOVED = -1
NEVER = 0
SOMETIMES = 1
ALWAYS = 2


def matching_structure(matching: BipartiteMatching) -> tuple[list[int], list[int], list[int]]:
    """
    各辺・左頂点・右頂点が最大マッチングで
    NEVER / SOMETIMES / ALWAYS のどれかを返す。

    戻り値は (edge_status, left_status, right_status)。
    edge_status は辺番号をそのまま添字に使い、削除済み辺は REMOVED とする。
    """
    matching.solve()

    n_left = matching.n_left
    n_right = matching.n_right
    s = n_left + n_right
    t = s + 1

    edges = matching.edges()
    mate_left, mate_right = matching.mates()
    matching_edge_ids = set(matching.matching_edge_ids())

    _, comp, _ = find_SCC(matching.residual_graph())

    edge_status = [REMOVED] * matching.edge_count()
    for edge_id, left, right in edges:
        r = n_left + right
        if comp[left] == comp[r]:
            edge_status[edge_id] = SOMETIMES
        elif edge_id in matching_edge_ids:
            edge_status[edge_id] = ALWAYS
        else:
            edge_status[edge_id] = NEVER

    left_status = [NEVER] * n_left
    for left, right in enumerate(mate_left):
        if comp[s] == comp[left]:
            left_status[left] = SOMETIMES
        elif right != -1:
            left_status[left] = ALWAYS

    right_status = [NEVER] * n_right
    for right, left in enumerate(mate_right):
        r = n_left + right
        if comp[r] == comp[t]:
            right_status[right] = SOMETIMES
        elif left != -1:
            right_status[right] = ALWAYS

    return edge_status, left_status, right_status


def general_matching_structure(
    matching: GeneralBipartiteMatching,
) -> tuple[list[int], list[int]]:
    """
    各辺・頂点が最大マッチングで
    NEVER / SOMETIMES / ALWAYS のどれかを返す。

    戻り値は (edge_status, vertex_status)。
    頂点番号・辺番号は入力時の番号をそのまま使う。
    """
    matching.solve()
    assert matching._matching is not None

    edge_status, left_status, right_status = matching_structure(matching._matching)

    vertex_status = [NEVER] * matching.n
    for left, v in enumerate(matching.fromL):
        vertex_status[v] = left_status[left]
    for right, v in enumerate(matching.fromR):
        vertex_status[v] = right_status[right]

    return edge_status, vertex_status


class DulmageMendelsohn:
    """
    二部マッチングを容量 1, inf, 1 の s-t フローに読み替え、
    全最小カットの構造から Dulmage--Mendelsohn 分解を求める。

    頂点番号は左 0..n_left-1、右 n_left..n_left+n_right-1、
    その後に s, t を置く。

    DM 分解は
      V0     : t へ残余路で到達可能な固定領域
      V1,... : V0, Vinf の外側にある SCC
      Vinf   : s から残余路で到達可能な固定領域
    からなる。

    API:
      DM.groups          : [V0, V1, ..., Vinf] のリスト
      DM.groupnum[v]     : 統合頂点 v が属する group の番号
      DM.left_groupnum   : 各左頂点が属する group の番号
      DM.right_groupnum  : 各右頂点が属する group の番号
      DM.dag             : groups を縮約した残余 DAG
      DM.V0, DM.Vinf     : 両端の固定領域
      DM.blocks          : [V1, V2, ...] のリスト

    groups, groupnum, dag では右頂点 right を n_left + right として扱う。
    groups は DAG のトポロジカル順に並び、dag の辺は小さい番号から大きい番号へ向かう。
    残余グラフ自体の細かい SCC は residual_graph, scc_groups, scc_comp, scc_dag に残す。

    GeneralBipartiteMatching に対して用いる場合は、solve() 後の
    _matching に入っている BipartiteMatching を渡せばよい。
    """

    def __init__(self, matching: BipartiteMatching) -> None:
        """最大マッチングから容量 1, inf, 1 の残余グラフを作り、DM 分解を求める。"""
        matching.solve()

        self.n_left = matching.n_left
        self.n_right = matching.n_right
        self.n = self.n_left + self.n_right
        self.s = self.n
        self.t = self.s + 1

        self.residual_graph = matching.residual_graph(middle_capacity_inf=True)
        self.scc_groups, self.scc_comp, self.scc_dag = find_SCC(self.residual_graph)

        k_scc = len(self.scc_groups)
        s_scc = self.scc_comp[self.s]
        t_scc = self.scc_comp[self.t]

        # 最大流後なので s から t への残余路はない。
        assert s_scc != t_scc

        source_reachable = [False] * k_scc
        stack = [s_scc]
        source_reachable[s_scc] = True
        while stack:
            c = stack.pop()
            for d in self.scc_dag[c]:
                if not source_reachable[d]:
                    source_reachable[d] = True
                    stack.append(d)

        rev = [[] for _ in range(k_scc)]
        for c in range(k_scc):
            for d in self.scc_dag[c]:
                rev[d].append(c)

        sink_reachable = [False] * k_scc
        stack = [t_scc]
        sink_reachable[t_scc] = True
        while stack:
            c = stack.pop()
            for d in rev[c]:
                if not sink_reachable[d]:
                    sink_reachable[d] = True
                    stack.append(d)

        # V0, Vinf は固定領域全体として一つにまとめ、自由領域だけ SCC を保つ。
        free_scc = [
            c for c in range(k_scc)
            if not source_reachable[c] and not sink_reachable[c]
        ]
        free_id = [-1] * k_scc
        for i, c in enumerate(free_scc):
            free_id[c] = i

        self.V0 = [
            v for v in range(self.n)
            if sink_reachable[self.scc_comp[v]]
        ]
        self.blocks = [
            [v for v in self.scc_groups[c] if v < self.n]
            for c in free_scc
        ]
        self.Vinf = [
            v for v in range(self.n)
            if source_reachable[self.scc_comp[v]]
        ]

        k = len(self.blocks)
        self.groups = [self.V0] + self.blocks + [self.Vinf]

        dm_of_scc = [-1] * k_scc
        for c in range(k_scc):
            if sink_reachable[c]:
                dm_of_scc[c] = 0
            elif source_reachable[c]:
                dm_of_scc[c] = k + 1
            else:
                dm_of_scc[c] = 1 + free_id[c]

        self.groupnum = [dm_of_scc[self.scc_comp[v]] for v in range(self.n)]
        self.left_groupnum = self.groupnum[:self.n_left]
        self.right_groupnum = self.groupnum[self.n_left:]

        # V0 と Vinf をそれぞれ一頂点に縮約した DM の DAG。
        dag = [[] for _ in range(k + 2)]
        seen = [set() for _ in range(k + 2)]
        for c in range(k_scc):
            a = dm_of_scc[c]
            for d in self.scc_dag[c]:
                b = dm_of_scc[d]
                if a != b and b not in seen[a]:
                    seen[a].add(b)
                    dag[a].append(b)
        self.dag = dag