# competitive-verifier: TITLE ポテンシャル付きUnionFind

class PotentialUnionFind:
    """連結成分と頂点間の加法的なポテンシャル差を管理する。"""
    def __init__(self, n):
        """n 個の単集合を作り、各頂点の相対ポテンシャルを零にする。"""
        self.parent = list(range(n)) #親ノード
        self.gsize = [1]*n #グループの要素数
        self.diff_p = [0]*n #p(x)-p(parent[x]) = diff_p(x) （親ノード（根でない）を基準としたポテンシャル・根ノードではない
    
    def root(self, x): #root(x): xの根ノードを返す．
        """指定した要素が属する集合の根を返す。"""
        while self.parent[x] != x:
            self.diff_p[x] += self.diff_p[self.parent[x]]
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x 
 
    def weight(self, x): # x のポテンシャル値を返す
        """根を基準とした頂点 x の加法的ポテンシャルを返す。"""
        c = 0
        while self.parent[x] != x:
            self.diff_p[x] += self.diff_p[self.parent[x]]
            self.parent[x] = self.parent[self.parent[x]]
            c += self.diff_p[x]
            x = self.parent[x]
        return c
 
    def merge(self, x, y, dxy): #ポテンシャル差p(x)-p(y)=dxyでxとyの組をまとめる
        """p(x)-p(y)=dxy の関係で二集合を併合し、代表元または併合済みを表す -1 を返す。"""
        dxy = self.weight(x) - self.weight(y) - dxy # p(rx)-p(ry)
        x,y = self.root(x), self.root(y)
        if x == y: return -1
        if self.gsize[x] < self.gsize[y]: #rxの要素数が大きいように
            x,y = y,x
            dxy = -dxy
        self.gsize[x] += self.gsize[y] #xの要素数を更新
        self.parent[y] = x #ryをrxにつなぐ
        self.diff_p[y] = dxy #ryの相対ポテンシャルを更新
        return x
 
    def issame(self, x, y): #same(x,y): xとyが同じ組ならTrue
        """二つの要素が同じ集合に属するかを返す。"""
        return self.root(x) == self.root(y)
        
    def diff(self,x,y): #diff(x,y): weight(x)-weight(y) を返す 
        """同じ成分の頂点について weight(x)-weight(y) を返す。"""
        return self.weight(x) - self.weight(y)

    def size(self,x): #size(x): xのいるグループの要素数を返す
        """指定した要素が属する集合の要素数を返す。"""
        return self.gsize[self.root(x)]
 
# https://atcoder.jp/contests/typical90/submissions/23631078
