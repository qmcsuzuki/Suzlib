# competitive-verifier: TITLE 静的区間和（累積和）


class StaticRangeSum:
    """累積和によって静的な半開区間の和を求める。"""
    def __init__(self, init):
        """初期列の末尾に零を置き、右からの累積和を構築する。"""
        acc = self.acc = list(init)
        acc.append(0)
        for i in range(len(acc)-2)[::-1]: # 右から累積和
            acc[i] += acc[i+1]

    def range_sum(self, l, r):
        """ 半閉区間 [l,r) 上の和 a[l] + ... + a[r-1] を返す """
        assert l <= r
        return self.acc[l] - self.acc[r]
