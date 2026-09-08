# competitive-verifier: TITLE モノイド付きUnionFind/ 辺数カウント（as 特殊化）

from python.data_structure.unionfind.UnionFind import UnionFind
class UnionFindMonoid(UnionFind):
    """集合の併合と各成分のモノイド集約値を管理する。"""
    # UF = UnionFindMonoid(n,op,init)
    def __init__(self, n, op, init):
        """n 個の単集合を作り、集約演算と各成分の初期値を設定する。"""
        super().__init__(n)
        self.op = op
        assert len(init)==n
        self.data = init[::]

    def merge(self, x, y): #merge(x,y): xのいる組とyのいる組をまとめる
        """二集合と集約値を併合し、代表元または併合済みを表す -1 を返す。"""
        x, y = self.leader(x), self.leader(y)
        if x == y: return -1
        if self.size[x] < self.size[y]: #xの要素数が大きいように
            x,y=y,x
        # yを x につなぐ
        self.size[x] += self.size[y]
        self.parent[y] = x
        self.data[x] = self.op(self.data[x], self.data[y])
        return x

    def add_value(self, x, val): # 頂点 x の連結成分の管理する値に val を足す
        """指定した頂点の成分の集約値に val を演算で合成する。"""
        x = self.leader(x)
        self.data[x] = self.op(self.data[x], val)
    
    def set_value(self, x, val): # 頂点 x の連結成分の管理する値を val に変更
        """指定した頂点の成分の集約値を val に上書きする。"""
        self.data[self.leader(x)] = val

    def get_value(self, x): # 頂点 x を含む連結成分の管理する値を取得
        """指定した頂点の成分が持つ集約値を返す。"""
        return self.data[self.leader(x)]

class UnionFindEdgeNum(UnionFindMonoid):
    """辺の追加に伴う連結成分と各成分の辺数を管理する。"""
    # 各連結成分の辺数を管理する UnionFind.
    # グラフに辺 (u, v) を追加するときは add_edge(u, v) を使う。

    def __init__(self, n):
        """n 個の孤立頂点を作り、各連結成分の辺数を零にする。"""
        super().__init__(n, int.__add__, [0] * n)

    def add_edge(self, x, y):
        """辺を一本追加して成分を併合し、成分の辺数を更新する。"""
        # 辺 (x, y) を 1 本追加する。
        self.add_value(x, 1)
        return super().merge(x, y)

    def merge(self, x, y):
        """直接の併合を禁止し、add_edge の使用を促す例外を送出する。"""
        raise AttributeError("UnionFindEdgeNum.merge is disabled. Use add_edge(x, y) instead.")

    def get_edge_num(self, x):
        """指定した頂点の連結成分に含まれる辺数を返す。"""
        return self.get_value(x)


"""
例: マージテク

def op(x,y):
    x += y
    return x

init = [[] for _ in range(NUMBER_OF_VARIABLES)]
"""
