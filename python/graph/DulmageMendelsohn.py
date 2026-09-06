# competitive-verifier: TITLE Dulmage--Mendelsohn 分解

from python.graph.BipartiteMatching import BipartiteMatching
from python.graph.SCC import find_SCC


class DulmageMendelsohn:
    """
    二部マッチングを容量 1, inf, 1 の s-t フローに読み替え、
    全最小カットの構造を SCC と縮約 DAG で表す。

    頂点番号は左 0..n_left-1、右 n_left..n_left+n_right-1、
    その後に s, t を置く。

    各 SCC の state は
      SOURCE: 全ての最小カットで source 側
      FREE  : 最小カットによって source / sink のどちらにもなり得る
      SINK  : 全ての最小カットで sink 側
    を表す。
    """

    SOURCE = 0
    FREE = 1
    SINK = 2

    def __init__(self, matching: BipartiteMatching) -> None:
        matching.solve()

        self.n_left = matching.n_left
        self.n_right = matching.n_right
        self.s = self.n_left + self.n_right
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
        self.groups, self.comp, self.dag = find_SCC(g)

        k = len(self.groups)
        s_comp = self.comp[self.s]
        t_comp = self.comp[self.t]
        self.s_comp = s_comp
        self.t_comp = t_comp

        # 最大流後なので s から t への残余路はない。
        assert s_comp != t_comp

        source_reachable = [False] * k
        stack = [s_comp]
        source_reachable[s_comp] = True
        while stack:
            c = stack.pop()
            for d in self.dag[c]:
                if not source_reachable[d]:
                    source_reachable[d] = True
                    stack.append(d)

        rev = [[] for _ in range(k)]
        for c in range(k):
            for d in self.dag[c]:
                rev[d].append(c)

        sink_reachable = [False] * k
        stack = [t_comp]
        sink_reachable[t_comp] = True
        while stack:
            c = stack.pop()
            for d in rev[c]:
                if not sink_reachable[d]:
                    sink_reachable[d] = True
                    stack.append(d)

        self.state = [self.FREE] * k
        for c in range(k):
            if source_reachable[c]:
                self.state[c] = self.SOURCE
            elif sink_reachable[c]:
                self.state[c] = self.SINK

        self.left_state = [self.state[self.comp[left]] for left in range(self.n_left)]
        self.right_state = [
            self.state[self.comp[self.n_left + right]]
            for right in range(self.n_right)
        ]
