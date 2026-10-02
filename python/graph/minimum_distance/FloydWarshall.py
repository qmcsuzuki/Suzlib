# competitive-verifier: TITLE フロイド・ワーシャル法

"""
辺重みは非負。有限距離は INF 未満を仮定する。
add_edge で辺を登録し、build を一度呼んでから距離を取得する。
build は O(V^3)、辺追加による更新は O(V^2)、距離取得は O(1)。空間 O(V^2)。
"""
class FloydWarshall:
    """重み付き有向グラフの全頂点対最短距離を管理する。"""
    INF = 1<<60
    def __init__(self,n):
        """対角を零、他を INF とする n 頂点の距離行列を用意する。"""
        D = self.D = [[self.INF]*n for _ in range(n)]
        for i in range(n): D[i][i] = 0
        self.built = False
        
    def add_edge(self,i,j,v):
        """構築前のグラフに重み v の有向辺 i -> j を登録する。"""
        self.D[i][j] = min(self.D[i][j],v)

    def build(self):
        """フロイド・ワーシャル法で全頂点対の最短距離を一度だけ計算する。"""
        n = len(self.D)
        assert not self.built
        self.built = True
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    self.D[i][j] = min(self.D[i][j], self.D[i][k]+ self.D[k][j])
    
    def dist(self,i,j):
        """構築済みの距離行列から i から j への最短距離を返す。"""
        assert self.built
        return self.D[i][j]
    
    # O(N^2)
    def construct_edge_undirected(self,a,b,v):
        """無向辺を一本追加し、全頂点対最短距離を二乗時間で更新する。"""
        n = len(self.D)
        assert self.built
        if v >= self.D[a][b] and v >= self.D[b][a]: return
        self.D[a][b] = min(self.D[a][b], v)
        self.D[b][a] = min(self.D[b][a], v)
        for i in range(n):
            for j in range(n):
                self.D[i][j] = min(self.D[i][j],
                                  self.D[i][a]+v+self.D[b][j],
                                  self.D[i][b]+v+self.D[a][j])
    
    def construct_edge_directed(self,a,b,v):
        """有向辺を一本追加し、全頂点対最短距離を二乗時間で更新する。"""
        assert self.built
        n = len(self.D)
        if v >= self.D[a][b]: return
        self.D[a][b] = v
        for i in range(n):
            for j in range(n):
                self.D[i][j] = min(self.D[i][j], self.D[i][a]+v+self.D[b][j])

#https://atcoder.jp/contests/abc375/submissions/62162410
