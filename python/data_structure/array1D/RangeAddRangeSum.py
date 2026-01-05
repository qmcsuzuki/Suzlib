# verification-helper: TITLE 区間加算・区間和 (Range Add Range Sum)

class RangeAddRangeSum():
    def __init__(self, n, init=None):
        if init is not None:
            init = list(init) + [0]
        self.bit0 = FenwickTree(n+1,init)
        self.bit1 = FenwickTree(n+1)

    def range_add(self,l,r,x):
        self.bit0.add(l,-l*x)
        self.bit0.add(r,r*x)
        self.bit1.add(l,x)
        self.bit1.add(r,-x)

    # 半開区間 [0,r) 上の和
    def prefix_sum(self,r):
        return self.bit1.prefix_sum(r)*r + self.bit0.prefix_sum(r)

    def range_sum(self,l,r):
        return self.prefix_sum(r) - self.prefix_sum(l)
    
    def point_get(self,i):
        return self.range_sum(i,i+1)
