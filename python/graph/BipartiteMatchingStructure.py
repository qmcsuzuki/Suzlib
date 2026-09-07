# competitive-verifier: TITLE 二部マッチングの構造

"""
DM分解、マッチングに使う辺・頂点
"""

from python.graph.BipartiteMatching import BipartiteMatching
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

    g = [[] for _ in range(t + 1)]

    # s -> left は容量 1。
    for left, right in enumerate(mate_left):
        if right == -1:
            g[s].append(left)
        else:
            g[left].append(s)

    # left -> right も容量 1。
    # 現在のマッチング辺だけ逆向き、それ以外は順向きが残余辺になる。
    for edge_id, left, right in edges:
        r = n_left + right
        if edge_id in matching_edge_ids:
            g[r].append(left)
        else:
            g[left].append(r)

    # right -> t は容量 1。
    for right, left in enumerate(mate_right):
        r = n_left + right
        if left == -1:
            g[r].append(t)
        else:
            g[t].append(r)

    _, comp, _ = find_SCC(g)

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


class DulmageMendelsohn:
    """
    二部マッチングを容量 1, inf, 1 の s-t フローに読み替え、
    全最小カットの構造から Dulmage--Mendelsohn 分解を求める。

    頂点番号は左 0..n_left-1、右 n_left..n_left+n_right-1、
    その後に s, t を置く。

    DM 分解は
      V0     : s から残余路で到達可能な固定領域
      blocks : V0, Vinf の外側にある SCC
      Vinf   : t へ残余路で到達可能な固定領域
    からなる。

    groups = [V0] + blocks + [Vinf] とし、comp, dag もこの番号を使う。
    残余グラフ自体の細かい SCC は scc_groups, scc_comp, scc_dag に残す。
    """

    SOURCE = 0
    FREE = 1
    SINK = 2

    def __init__(self, matching: BipartiteMatching) -> None:
        """最大マッチングから容量 1, inf, 1 の残余グラフを作り、DM 分解を求める。"""
        matching.solve()

        self.n_left = matching.n_left
        self.n_right = matching.n_right
        self.n = self.n_left + self.n_right
        self.s = self.n
        self.t = self.s + 1

        self.edges = matching.edges()
        self.mate_left, self.mate_right = matching.mates()

        g = [[] for _ in range(self.t + 1)]

        # s -> left は容量 1。
        for left, right in enumerate(self.mate_left):
            if right == -1:
                g[self.s].append(left)
            else:
                g[left].append(self.s)

        # left -> right は容量 inf なので、マッチング辺でも順向き残余辺が残る。
        # マッチング辺にはさらに逆向き残余辺がある。
        matched = set(matching.matching_edge_ids())
        for edge_id, left, right in self.edges:
            r = self.n_left + right
            g[left].append(r)
            if edge_id in matched:
                g[r].append(left)

        # right -> t は容量 1。
        for right, left in enumerate(self.mate_right):
            r = self.n_left + right
            if left == -1:
                g[r].append(self.t)
            else:
                g[self.t].append(r)

        self.residual_graph = g
        self.scc_groups, self.scc_comp, self.scc_dag = find_SCC(g)

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

        scc_state = [self.FREE] * k_scc
        for c in range(k_scc):
            if source_reachable[c]:
                scc_state[c] = self.SOURCE
            elif sink_reachable[c]:
                scc_state[c] = self.SINK
        self.scc_state = scc_state

        # V0, Vinf は固定領域全体として一つにまとめ、自由領域だけ SCC を保つ。
        free_scc = [c for c in range(k_scc) if scc_state[c] == self.FREE]
        free_id = [-1] * k_scc
        for i, c in enumerate(free_scc):
            free_id[c] = i

        self.V0 = [v for v in range(self.n) if scc_state[self.scc_comp[v]] == self.SOURCE]
        self.blocks = [
            [v for v in self.scc_groups[c] if v < self.n]
            for c in free_scc
        ]
        self.Vinf = [v for v in range(self.n) if scc_state[self.scc_comp[v]] == self.SINK]

        k = len(self.blocks)
        self.groups = [self.V0] + self.blocks + [self.Vinf]
        self.s_comp = 0
        self.t_comp = k + 1

        dm_of_scc = [-1] * k_scc
        for c in range(k_scc):
            if scc_state[c] == self.SOURCE:
                dm_of_scc[c] = self.s_comp
            elif scc_state[c] == self.SINK:
                dm_of_scc[c] = self.t_comp
            else:
                dm_of_scc[c] = 1 + free_id[c]

        self.comp = [dm_of_scc[self.scc_comp[v]] for v in range(self.n)]

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

        self.state = [self.SOURCE] + [self.FREE] * k + [self.SINK]
        self.left_state = [self.state[self.comp[left]] for left in range(self.n_left)]
        self.right_state = [
            self.state[self.comp[self.n_left + right]]
            for right in range(self.n_right)
        ]
