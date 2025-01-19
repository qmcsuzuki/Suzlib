class RangeAddPointGet(FenwickTree):
    def __init__(self, n, init=None):
        if init is not None:
            init = list(init) + [0]
            for i in range(1,n)[::-1]:
                init[i] -= init[i-1]
        super().__init__(n+1,init)
        
    def range_add(self,l,r,x):
        self.add(l,x)        
        self.add(r,-x)
    
    def point_get(self,i):
        return self.prefix_sum(i+1)
