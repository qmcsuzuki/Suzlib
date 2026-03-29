# competitive-verifier: TITLE 二部グラフ判定

from python.data_structure.unionfind.UnionFind import UnionFind

class bipartite:
    def __init__(self, n):
        self.n = n
        self.UF = UnionFind(2 * n)
        self.is_bipartite = True
        self.num_conn_comp = n # 元のグラフの連結成分数
        # UF の各 root について、その集合に含まれる「元の頂点 0..n-1」の個数
        self.orig_vertex_count = [1] * n + [0] * n

    def _merge(self, x, y):
        x, y = self.UF.leader(x), self.UF.leader(y)
        if x == y:
            return -1
        if self.UF.size[x] < self.UF.size[y]:
            x, y = y, x
        self.UF.size[x] += self.UF.size[y]
        self.UF.parent[y] = x
        self.orig_vertex_count[x] += self.orig_vertex_count[y]
        return x

    def is_connected(self, u, v):
        return self.UF.issame(u, v) or self.UF.issame(u, v + self.n)

    def component_is_bipartite(self, v):
        return not self.UF.issame(v, v + self.n)

    def connected_color_relation(self, u, v):
        """
        u, v の関係を返す
          0   : 非連結
          1   : 同じ連結成分で同色
         -1   : 同じ連結成分で異色
          None: 同じ連結成分だが、その成分は二部グラフでない
        """
        if not self.is_connected(u, v):
            return 0
        if self.UF.issame(u, u + self.n):
            return None
        return 1 if self.UF.issame(u, v) else -1

    def add_edge(self, u, v):
        # 元のグラフの連結成分数の更新
        if not self.is_connected(u, v):
            self.num_conn_comp -= 1

        # u, v は異色
        self._merge(u, v + self.n)
        self._merge(u + self.n, v)

        if self.UF.issame(u, u + self.n):
            self.is_bipartite = False

    def add_same(self, u, v):
        # 元のグラフの連結成分数の更新
        if not self.is_connected(u, v):
            self.num_conn_comp -= 1

        # u, v は同色
        self._merge(u, v)
        self._merge(u + self.n, v + self.n)

        if self.UF.issame(u, u + self.n):
            self.is_bipartite = False

    def coloring(self):
        """
        01 二値の色配列を返す。各連結成分ごとに、leader(v) < leader(v+n) 側を色 0 とする
        """
        assert self.component_is_bipartite(v)

        col = [0] * self.n
        for v in range(self.n):
            col[v] = 0 if self.UF.leader(v) < self.UF.leader(v + self.n) else 1
        return col

    def connected_component_color_sizes(self, v):
        """
        v を含む連結成分について、
        coloring() と同じ規約で (色0の個数, 色1の個数) を返す。
        """
        assert self.component_is_bipartite(v)

        r0 = self.UF.leader(v)
        r1 = self.UF.leader(v + self.n)
        x = self.orig_vertex_count[r0]
        y = self.orig_vertex_count[r1]
        return (x, y) if r0 < r1 else (y, x)

def all_connected_components(self):
    """
    全ての連結成分についての (色0頂点の個数, 色1頂点の個数) のリストを返す
    色0/1 の規約は coloring() と同じ
    """
    res = []
    used = [0] * (2 * self.n)
    for v in range(self.n):
        r0 = self.UF.leader(v)
        r1 = self.UF.leader(v + self.n)
        rep = r0 if r0 < r1 else r1
        if used[rep]:
            continue
        used[rep] = 1
        res.append(self.connected_component_color_sizes(v))
    return res

    def number_of_connected_component(self):
        return self.num_conn_comp
