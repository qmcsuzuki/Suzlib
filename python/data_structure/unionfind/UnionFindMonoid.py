# competitive-verifier: TITLE モノイド付きUnionFind

from python.data_structure.unionfind.UnionFind import UnionFind
class UnionFindMonoid(UnionFind):
    # UF = UnionFindMonoid(n,op,init)
    def __init__(self, n, op, init):
        super().__init__(n)
        self.op = op
        assert len(init)==n
        self.data = init[::]

    def merge(self, x, y): #merge(x,y): xのいる組とyのいる組をまとめる
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
        x = self.leader(x)
        self.data[x] = self.op(self.data[x], val)
    
    def set_value(self, x, val): # 頂点 x の連結成分の管理する値を val に変更
        self.data[self.leader(x)] = val

    def get_value(self, x): # 頂点 x を含む連結成分の管理する値を取得
        return self.data[self.leader(x)]

"""
例: マージテク

def op(x,y):
    x += y
    return x

init = [[] for _ in range(NUMBER_OF_VARIABLES)]
"""
