class SegmentTree:
    # seg = SegmentTree(N,op,e,init=None)
    def __init__(self, N, operator_M, e_M, init=None):
        self.op_M = operator_M
        self.e_M = e_M
        self.N = N
        self.N0 = 1<<(N-1).bit_length()
        self.data = [self.e_M]*(2*self.N0)
        if init is not None:
            assert N == len(init)
            self.data[self.N0:self.N0+len(init)] = init[:]
            for k in range(self.N0)[::-1]:
                self.data[k] = self.op_M(self.data[2*k], self.data[2*k+1])

    # a_k の値を x に更新
    def update(self,k,x):
        k += self.N0
        self.data[k] = x
        k >>= 1
        while k:
            self.data[k] = self.op_M(self.data[2*k], self.data[2*k+1])
            k >>= 1

    # 区間[L,R)をopでまとめる
    def query(self,L,R):
        L += self.N0; R += self.N0
        sl = sr = self.e_M
        while L < R:
            if R & 1:
                R -= 1
                sr = self.op_M(self.data[R],sr)
            if L & 1:
                sl = self.op_M(sl,self.data[L])
                L += 1
            L >>= 1; R >>= 1
        return self.op_M(sl,sr)

    def __getitem__(self, k): #k番目の値を取得。
        return self.data[k+self.N0]
    
    """
    f(x_l*...*x_{r-1}) が True になる最大の r 
    つまり TTTTFFFF となるとき、F となる最小の添え字
    存在しない場合 n が返る
    f(e_M) = True でないと壊れる
    """
    def max_right(self,l,f):
        if l == self.N: return self.N;
        l += self.N0
        sm = self.e_M
        while True:
            while l&1==0:
                l >>= 1
            
            if not f(self.op_M(sm,self.data[l])):
                while l < self.N0:
                    l *= 2
                    if f(self.op_M(sm,self.data[l])):
                        sm = self.op_M(sm,self.data[l])
                        l += 1
                return l - self.N0

            sm = self.op_M(sm,self.data[l])
            l += 1
            if (l & -l) == l: break
        
        return self.N

    """
    f(x_l*...*x_{r-1}) が True になる最小の l
    つまり FFFFTTTT となるとき、T となる最小の添え字
    存在しない場合 r が返る
    f(e_M) = True でないと壊れる
    """
    def min_left(self,r,f):
        if r == 0: return 0
        r += self.N0
        sm = self.e_M
        
        while True:
            r -= 1
            while r > 1 and r&1:
                r >>= 1

            if not f(self.op_M(self.data[r],sm)):
                while r < self.N0:
                    r = r*2 + 1
                    if f(self.op_M(self.data[r],sm)):
                        sm = self.op_M(self.data[r],sm)
                        r -= 1
                return r + 1 - self.N0

            sm = self.op_M(self.data[r],sm)
            if (r & -r) == r: break

        return 0

# https://atcoder.jp/contests/practice2/submissions/61843395
