# competitive-verifier: TITLE 動的 Fenwick 木（使うとこだけ作る Fenwick 木）

"""
n: とりうる値の最大値
"""
class FenwickTreeDinamic: #0-indexed
    def __init__(self, n):
        self.tree = {}
        self.MAX = 1<<(n+1).bit_length()
    def get_sum(self, i): #a_0 + ... + a_{i} #閉区間
        s = 0; i += 1
        while i > 0:
            if i in self.tree:
                s += self.tree[i]
            i -= i & -i
        return s
    def query(self,l,r): #a_l + ... + a_r 閉区間
        return self.get_sum(r) - self.get_sum(l-1) 
    def add(self, i, x):
        i += 1
        while i <= self.MAX:
            if i in self.tree:
                self.tree[i] += x
            else:
                self.tree[i] = x
            i += i & -i
    def bisect_left(self,w):
        #和が w 以上になる最小の index
        #w が存在しない場合 -1 を返す
        if w <= 0: return 0
        x,k = 0,self.MAX
        while k:
            k >>= 1
            if x+k not in self.tree:
                x += k
            elif self.tree[x+k] < w:
                w -= self.tree[x+k]
                x += k
        return x if x!=self.MAX-1 else -1
