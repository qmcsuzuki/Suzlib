# competitive-verifier: TITLE 静的長方形加算（最後に各点の値を求める）


class StaticRectangleAdd:
    """
    H*W の長方形加算
    最後に和を計算する
    """
    def __init__(self,H,W):
        self.H = H
        self.W = W
        self.data = [[0]*(W+1) for _ in range(H+1)]

    def add_rectangle(self,h1,h2,w1,w2,val):
        """半開長方形 [h1:h2]*[w1:w2] 上に val を加える"""
        self.data[h1][w1] += val
        self.data[h1][w2] -= val
        self.data[h2][w1] -= val
        self.data[h2][w2] += val
    
    def solve(self):
        """各点の値を求める（１回しかできない）"""
        for lst in self.data:
            for j in range(self.W):
                lst[j+1] += lst[j]
        
        for i in range(self.H):
            for j in range(self.W):
                self.data[i+1][j] += self.data[i][j]
        
        return [self.data[i][:-1] for i in range(self.H)]
