# verification-helper: TITLE 等差数列加算（最後に全体の値が分かればよい）

class StaticSegmentAdd:
    def __init__(self, n):
        self.n = n
        self.data = [0]*(n+2)
        
    def add_segment(self,a,b,p,q):
        """ 半開区間 [p,q) に等差数列 a(x-p) + b を加える"""
        assert q <= self.n
        if p >= q: return
        self.data[p] += b
        self.data[p+1] += a-b
        y = a*(q-1-p)+b
        self.data[q] += -y-a
        self.data[q+1] += y
    
    def solve(self):
        """各点の値を求める（１回しかできない）"""
        for i in range(self.n):
            self.data[i+1] += self.data[i]
        for i in range(self.n):
            self.data[i+1] += self.data[i]
        return self.data[:self.n]

# https://atcoder.jp/contests/abc407/submissions/66141796
