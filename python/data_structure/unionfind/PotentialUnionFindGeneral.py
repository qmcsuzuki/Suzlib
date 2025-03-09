class PotentialUnionFindGeneral:
    def __init__(self, n, add, inv, e_M):
        self.parent = [-1]*n #親ノード or size
        self.potential = [e_M]*n #親ノードを基準としたポテンシャル
        self.add = add #足し算
        self.inv = inv #逆元
        self.e_M = e_M #単位元

    def root(self, x): #root(x): xの根ノードを返す．
        while self.parent[x] >= 0:
            x = self.parent[x]
        return x 

    def weight(self, x): # p(x) - p(root)
        c = self.e_M
        while self.parent[x] >= 0:
            c = self.add(self.potential[x], c)
            x = self.parent[x]
        return c

    def merge(self, x, y, dxy): #ポテンシャル差p(x)-p(y)=dxyでxとyの組をまとめる
        dxy = self.add(self.add(self.weight(x),dxy), self.inv(self.weight(y))) #dxyを置き換え
        x,y = self.root(x), self.root(y)
        if x == y: return False
        if self.parent[x] > self.parent[y]: #rxの要素数が大きいように
            x,y = y,x
            dxy = self.inv(dxy)
        self.parent[x] += self.parent[y] #xの要素数を更新
        self.parent[y] = x #ryをrxにつなぐ
        self.potential[y] = dxy #ryの相対ポテンシャルを更新
        return True
 
    def issame(self, x, y): #same(x,y): xとyが同じ組ならTrue
        return self.root(x) == self.root(y)
        
    def diff(self,x,y): #diff(x,y): wt(x)-wt(y) を返す 
        return self.add(self.weight(x), self.inv(self.weight(y)))

    def size(self,x): #size(x): xのいるグループの要素数を返す
        return -self.parent[self.root(x)]
