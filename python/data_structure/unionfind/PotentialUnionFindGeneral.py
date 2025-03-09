class PotentialUnionFindGeneral:
    def __init__(self, n, mul, inv, e_M):
        self.parent = [-1]*n #親ノード or size
        self.diff_p = [e_M]*n # p(x) = p(parent[x])*diff_p(x) （親ノードを基準としたポテンシャル・根ノードではない）
        self.mul = mul #積
        self.inv = inv #逆元
        self.e_M = e_M #単位元

    def root(self, x): #root(x): xの根ノードを返す．
        while self.parent[x] >= 0:
            x = self.parent[x]
        return x 

    def weight(self, x): # p(x) * p(root)^{-1}
        c = self.e_M
        while self.parent[x] >= 0:
            c = self.mul(self.diff_p[x], c)
            x = self.parent[x]
        return c

    def merge(self, x, y, dxy): #ポテンシャル差 p(x)=p(y)*dxy でxとyの組をまとめる
        dxy = self.mul(self.weight(x), self.inv(self.mul(self.weight(y), dxy))) #dxyを置き換え
        x,y = self.root(x), self.root(y)
        if x == y: return False
        if self.parent[x] > self.parent[y]: #rxの要素数が大きいように
            x,y = y,x
            dxy = self.inv(dxy)
        self.parent[x] += self.parent[y] #xの要素数を更新
        self.parent[y] = x #ryをrxにつなぐ
        self.diff_p[y] = dxy #ryの相対ポテンシャルを更新
        return True
 
    def issame(self, x, y): #same(x,y): xとyが同じ組ならTrue
        return self.root(x) == self.root(y)
        
    def diff(self,x,y): #diff(x,y): wt(y)^{-1}*wt(x) を返す 
        return self.mul(self.inv(self.weight(y)), self.weight(x))

    def size(self,x): #size(x): xのいるグループの要素数を返す
        return -self.parent[self.root(x)]

