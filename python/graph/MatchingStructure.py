# competitive-verifier: TITLE 最大二部マッチングの構造

from python.graph.BipartiteMatching import BipartiteMatching
from python.graph.SCC import find_SCC


class MatchingStructure:
    """
    容量 1 の s-t フローネットワークの残余グラフから、
    辺・頂点が最大マッチングで NEVER / SOMETIMES / ALWAYS のどれかを求める。

    頂点番号は左 0..n_left-1、右 n_left..n_left+n_right-1、
    その後に s, t を置く。
    """

    REMOVED = -1
    NEVER = 0
    SOMETIMES = 1
    ALWAYS = 2

    def __init__(self, matching: BipartiteMatching) -> None:
        matching.solve()

        self.n_left = matching.n_left
        self.n_right = matching.n_right
        self.s = self.n_left + self.n_right
        self.t = self.s + 1

        self.edges = matching.edges()
        self.mate_left, self.mate_right = matching.mates()
        self.matching_edge_ids = set(matching.matching_edge_ids())

        g = [[] for _ in range(self.t + 1)]

        # s -> left は容量 1。
        for left, right in enumerate(self.mate_left):
            if right == -1:
                g[self.s].append(left)
            else:
                g[left].append(self.s)

        # left -> right も容量 1。
        # 現在のマッチング辺だけ逆向き、それ以外は順向きが残余辺になる。
        for edge_id, left, right in self.edges:
            r = self.n_left + right
            if edge_id in self.matching_edge_ids:
                g[r].append(left)
            else:
                g[left].append(r)

        # right -> t は容量 1。
        for right, left in enumerate(self.mate_right):
            r = self.n_left + right
            if left == -1:
                g[r].append(self.t)
            else:
                g[self.t].append(r)

        self.residual_graph = g
        self.groups, self.comp, self.dag = find_SCC(g)

        # edge_id をそのまま添字に使えるよう、削除済み辺は REMOVED のまま残す。
        self.edge_status = [self.REMOVED] * matching.edge_count()
        for edge_id, left, right in self.edges:
            r = self.n_left + right
            if self.comp[left] == self.comp[r]:
                self.edge_status[edge_id] = self.SOMETIMES
            elif edge_id in self.matching_edge_ids:
                self.edge_status[edge_id] = self.ALWAYS
            else:
                self.edge_status[edge_id] = self.NEVER

        self.left_status = [self.NEVER] * self.n_left
        for left, right in enumerate(self.mate_left):
            if self.comp[self.s] == self.comp[left]:
                self.left_status[left] = self.SOMETIMES
            elif right == -1:
                self.left_status[left] = self.NEVER
            else:
                self.left_status[left] = self.ALWAYS

        self.right_status = [self.NEVER] * self.n_right
        for right, left in enumerate(self.mate_right):
            r = self.n_left + right
            if self.comp[r] == self.comp[self.t]:
                self.right_status[right] = self.SOMETIMES
            elif left == -1:
                self.right_status[right] = self.NEVER
            else:
                self.right_status[right] = self.ALWAYS
