from python.data_structure.unionfind.UnionFind import UnionFind
class UnionFindMonoid(UnionFind):
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

"""
例: マージテク

def op(x,y):
    x += y
    return x

init = [[] for _ in range(NUMBER_OF_VARIABLES)]
"""
