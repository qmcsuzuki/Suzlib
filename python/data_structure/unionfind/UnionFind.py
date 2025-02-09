class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n)) #親ノード
        self.size = [1]*n #グループの要素数
 
    def leader(self, x): #leader(x): xの根ノードを返す．
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x 
 
    def merge(self, x, y): #merge(x,y): xのいる組とyのいる組をまとめる
        x, y = self.leader(x), self.leader(y)
        if x == y: return -1
        if self.size[x] < self.size[y]: #xの要素数が大きいように
            x,y=y,x
        # yを x につなぐ
        self.size[x] += self.size[y]
        self.parent[y] = x
        return x
 
    def issame(self, x, y): #same(x,y): xとyが同じ組ならTrue
        return self.leader(x) == self.leader(y)
        
    def getsize(self,x): #size(x): xのいるグループの要素数を返す
        return self.size[self.leader(x)]

    def all_leaders(self): # 全てのリーダーのリストを返す
        return [i for i,v in enumerate(self.parent) if i==v]
        
    def groups(self): # 全ての連結成分からなるリストを返す
        n = len(self.parent)
        gp = [[] for _ in range(n)]
        for v in range(n):
            gp[self.leader(v)].append(v)
        return [lst for lst in gp if lst]
