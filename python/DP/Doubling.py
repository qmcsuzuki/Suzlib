# competitive-verifier: TITLE ダブリング

class Doubling:
    def __init__(self, nxt, depth=61):
        self.D = depth # we have D rows
        self.table = [nxt]
        for _ in range(depth-1):
            nxt = [nxt[v] for v in nxt]
            self.table.append(nxt)

    # 入力: weights[k] = (k から１回移動するときの重み)
    # 計算: Wtable[k][v] = v から 2^k 回移動した時の重みの和
    def set_weight(self,weights,op,e):
        assert len(weights) == len(self.table[0])
        self.e = e
        self.op = op
        w = weights[:]
        self.Wtable = [w]
        for nxt in self.table:
            w = [op(w[i],w[v]) for i,v in enumerate(nxt)]
            self.Wtable.append(w)
    
    # f^k(v) を返す
    def kth_pos(self,k,v):
        for i, nxt in enumerate(self.table):
            if k>>i&1: v = nxt[v]
        return v

    # (w,f^k(v)): k 回移動したときの重みの和 w と最終位置 f^k(v) を返す
    def kth_weight_and_pos(self,k,v):
        w = self.e
        for i, nxt in enumerate(self.table):
            if k>>i&1:
                w = self.op(w, self.Wtable[i][v])
                v = nxt[v]
        return w,v


# example: https://atcoder.jp/contests/abc438/submissions/72051651

# nxt = [i-1 for i in a]
# wt = list(range(1,n+1))
# D = Doubling(nxt,31)
# D.set_weight(wt, int.__add__, 0)




