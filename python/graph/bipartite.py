# competitive-verifier: TITLE 二部グラフ判定

from python.data_structure.unionfind.UnionFind import UnionFind

class bipartite(UnionFind):
    def __init__(self, n):
        super().__init__(2 * n)
        self.n = n
        self.is_bipartite = True
        self.num_conn_comp = 2 * n # UnionFind 上での現在の連結成分数
        # 各 root を含む集合の「元の頂点 0..n-1」の個数
        self.orig_vertex_count = [1] * n + [0] * n

    def merge(self, x, y):  # merge(x,y): x のいる組と y のいる組をまとめる
        x, y = self.leader(x), self.leader(y)
        if x == y:
            return -1
        if self.size[x] < self.size[y]:  # x の要素数が大きいように
            x, y = y, x
        # y を x につなぐ
        self.size[x] += self.size[y]
        self.parent[y] = x
        self.orig_vertex_count[x] += self.orig_vertex_count[y]
        self.num_conn_comp -= 1
        return x

    def add_edge(self, u, v):  # 頂点 u,v を辺で結ぶ（違う色という情報を与える）
        self.merge(u, v + self.n)
        self.merge(u + self.n, v)
        if self.issame(u, u + self.n):
            self.is_bipartite = False

    def add_same(self, u, v):  # 頂点 u,v が同じ色という情報を与える
        self.merge(u, v)
        self.merge(u + self.n, v + self.n)
        if self.issame(u, u + self.n):
            self.is_bipartite = False

    def coloring(self):  # 二部グラフの色付けとなる、01 二値の配列を返す。
        col = [0] * self.n
        for v in range(self.n):
            col[v] = 0 if self.leader(v) < self.leader(v + self.n) else 1
        return col

    def connected_component_color_sizes(self, v):
        """
        v を含む連結成分について、
        coloring() と同じ規約で (色0の個数, 色1の個数) を返す。
        """
        r0 = self.leader(v)
        r1 = self.leader(v + self.n)
        x = self.orig_vertex_count[r0]
        y = self.orig_vertex_count[r1]
        return (x, y) if r0 < r1 else (y, x)

    def all_connected_components(self):
        """
        全ての連結成分についての（色0頂点の個数、色1頂点の個数）のペアのリストを返す
        色0/1 の規約は coloring() と同じ
        """
        res = []
        used = [0] * (2 * self.n)
        for v in range(self.n):
            r0 = self.leader(v)
            r1 = self.leader(v + self.n)
            rep = r0 if r0 < r1 else r1
            if used[rep]:
                continue
            used[rep] = 1
            x = self.orig_vertex_count[r0]
            y = self.orig_vertex_count[r1]
            res.append((x, y) if r0 < r1 else (y, x))
        return res

    def number_of_connected_component(self):  # 現在の連結成分数を返す O(1)
        return self.num_conn_comp // 2
