# competitive-verifier: TITLE XOR基底

"""
xor 基底を管理する
"""
class XorBasis:
    def __init__(self):
        self.basis = []

    def add_basis(self, x): # 基底集合に x を追加
        x = self.normalize(x)
        if x: self.basis.append(x)

    def normalize(self, x): # ベクトル x を基底で掃き出して標準化する
        for v in self.basis:
            if v^x < x:
                x ^= v
        return x
    
    def get_sorted_basis(self): # 降順ソートした基底を得る（貪欲法などに使用）
        sort(self.basis, reverse=1)
        return self.basis[::]

# https://atcoder.jp/contests/kupc2012/submissions/66800244
