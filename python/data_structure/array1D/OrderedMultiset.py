from bisect import bisect_left, bisect_right
class OrderedMultiset:
    def __init__(self, N, banhei): # 0 以上 N 以下
        # 番兵 -1 を FenwickTree の 0 として扱う、つまり外部の値 v では bit 内部の v+1 を操作することに注意
        assert banhei == N+1
        self.bit = FenwickTree(N+3) #存在すれば 1、しないなら 0
        self.add(-1)
        self.add(banhei)

    def __contains__(self,v):
        return self.bit.range_sum(v+1,v+2) > 0

    def add(self,v,wt=1): # 値 v を重み wt で追加（通常重み=1）
        self.bit.add(v+1,wt)
        
    def delete(self,v): # 値 v を削除
        self.add(v,-1)

    def kth_value(self,k):
        # k 番目 (1-indexed) に小さい元の値を求める。k が大きすぎると、範囲外エラーとなるので注意
        return self.bit.bisect_left(k+1) - 1

    def prev_value(self,v): #一個前の元の値
        s = self.bit.prefix_sum(v+1)
        return self.bit.bisect_left(s) - 1

    def next_value(self,v):
        s = self.bit.prefix_sum(v+2)
        return self.bit.bisect_left(s+1) - 1
