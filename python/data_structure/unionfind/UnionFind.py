# competitive-verifier: TITLE UnionFind

class UnionFind:
    """集合の併合と所属する集合の代表元・要素数を管理する。"""
    def __init__(self, n):
        """n 個の要素をそれぞれ独立した単集合として初期化する。"""
        self.parent = list(range(n)) #親ノード
        self.size = [1]*n #グループの要素数
 
    def leader(self, x): #leader(x): xの根ノードを返す．
        """指定した要素が属する集合の代表元を返す。"""
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x 
 
    def merge(self, x, y): #merge(x,y): xのいる組とyのいる組をまとめる
        """二集合を併合し、代表元または併合済みを表す -1 を返す。"""
        x, y = self.leader(x), self.leader(y)
        if x == y: return -1
        if self.size[x] < self.size[y]: #xの要素数が大きいように
            x,y=y,x
        # yを x につなぐ
        self.size[x] += self.size[y]
        self.parent[y] = x
        return x
 
    def issame(self, x, y): #same(x,y): xとyが同じ組ならTrue
        """二つの要素が同じ集合に属するかを返す。"""
        return self.leader(x) == self.leader(y)
        
    def getsize(self,x): #size(x): xのいるグループの要素数を返す
        """指定した要素が属する集合の要素数を返す。"""
        return self.size[self.leader(x)]

    def all_leaders(self): # 全てのリーダーのリストを返す
        """すべての集合の代表元をリストで返す。"""
        return [i for i,v in enumerate(self.parent) if i==v]
        
    def groups(self): # 全ての連結成分からなるリストを返す
        """同じ集合に属する要素をまとめたリストを返す。"""
        n = len(self.parent)
        gp = [[] for _ in range(n)]
        for v in range(n):
            gp[self.leader(v)].append(v)
        return [lst for lst in gp if lst]
