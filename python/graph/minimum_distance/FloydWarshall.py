"""
とりあえず辺の重みは非負
"""
class FloydWarshall:
    INF = 1<<60
    def __init__(self,n):
        D = self.D = [[self.INF]*n for _ in range(n)]
        for i in range(n): D[i][i] = 0
        
    def add_edge(self,i,j,v):
        self.D[i][j] = min(self.D[i][j],v)

    def solve(self):
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    self.D[i][j] = min(self.D[i][j], self.D[i][k]+ self.D[k][j])
    
    def dist(self,i,j):
        return self.D[i][j]
    
    # O(N^2)
    def shorten_edge_length_undirected(self,a,b,v):
        if v >= self.D[a][b]: return
        self.D[a][b] = self.D[b][a] = v
        for i in range(n):
            for j in range(n):
                self.D[i][j] = min(self.D[i][j],
                                  self.D[i][a]+v+self.D[b][j],
                                  self.D[i][b]+v+self.D[a][j])
    
    def shorten_edge_length_directed(self,a,b,v):
        if v >= self.D[a][b]: return
        self.D[a][b] = v
        for i in range(n):
            for j in range(n):
                self.D[i][j] = min(self.D[i][j], self.D[i][a]+v+self.D[b][j])

#https://atcoder.jp/contests/abc375/submissions/62162410
