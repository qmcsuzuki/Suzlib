# competitive-verifier: TITLE Steiner木

class SteinerTree:
    """少数の指定頂点を結ぶ最小シュタイナー木の重みを部分集合 DP で求める。"""
    def __init__(self,n):
        """n 頂点の辺のない重み付き無向グラフを作る。"""
        self.n = n
        self.g = [[] for _ in range(n)]
    
    def add_edge(self,u,v,c):
        """非負重み c の無向辺 u-v を追加する。"""
        assert c >= 0
        self.g[u].append((v,c))
        self.g[v].append((u,c))
    
    def solve(self,nodes):
        """指定頂点集合を結ぶ最小シュタイナー木の総重みを求める。"""
        INF = 1<<60
        g = self.g
        n = self.n
        k = len(nodes)
        from heapq import heapify,heappush,heappop
        """
        dp[S][v] = min cost to connect S and v
        """
        self.dp = dp = [[INF]*n for _ in range(1<<k)]
        for i,v in enumerate(nodes):
            dp[1<<i][v] = 0

        for S,dpS in enumerate(dp):
            # dp[S][v] <- chmin(dp[T][v]+dp[S-T][v]) for all T
            T = SS = S&(S-1) # ignore the least existing bit
            while T:
                for v in range(n):
                    dpS[v] = min(dpS[v], dp[T][v] + dp[S^T][v])
                T = SS&(T-1)
            # dp[S][u] <- chmin(dp[S][v]+cost(v,u)) for all v
            # similar to Dijkstra, fix dp[S][v] from small to large
            q = [(cv,v) for v,cv in enumerate(dpS)]
            heapify(q)
            while q:
                cv,v = heappop(q)
                if dpS[v] < cv: continue
                for u,c_edge in g[v]:
                    if (newcost := cv+c_edge) < dpS[u]:
                        dpS[u] = newcost
                        heappush(q,(newcost,u))
        return min(dp[-1])

# https://atcoder.jp/contests/abc364/submissions/62235876
