# competitive-verifier: TITLE XOR基底

"""
xor 基底を管理する
"""
class XorBasis:
    """整数の XOR 線形基底を管理する。"""
    def __init__(self):
        """空の XOR 線形基底を作る。"""
        self.basis = []

    def add_basis(self, x): # 基底集合に x を追加
        """整数を現在の XOR 基底で簡約し、独立なら基底に追加する。"""
        x = self.normalize(x)
        if x: self.basis.append(x)

    def normalize(self, x): # ベクトル x を基底で掃き出して標準化する
        """整数を現在の XOR 基底で簡約した値を返す。"""
        for v in self.basis:
            if v^x < x:
                x ^= v
        return x
    
    def get_sorted_basis(self): # 降順ソートした基底を得る（貪欲法などに使用）
        """XOR 基底を降順に並べた新しいリストを返す。"""
        self.basis.sort(reverse=True)
        return self.basis[::]

# https://atcoder.jp/contests/kupc2012/submissions/66800244
