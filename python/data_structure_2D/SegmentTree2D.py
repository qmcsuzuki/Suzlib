class SegmentTree2D:
    """ seg = SegmentTree2D(N,M,op,e,init=None) """
    def __init__(self, N,M, op, e, init=None):
        self.op = op
        self.e = e
        self.N = N
        self.M = M
        self.N0 = 2*N#1<<(N-1).bit_length()
        self.M0 = 2*M#1<<(M-1).bit_length()
        self.data = [[self.e]*(2*self.M0) for _ in range(2*self.N0)]
        if init is not None:
            assert N == len(init) and M == len(init[0])
            for n in range(self.N0,self.N0+N):
                self.data[n][self.M0:self.M0+M] = init[n-self.N0][:]
            for k in range(self.N0,self.N0+N)[::-1]:
                for l in range(self.M0)[::-1]:
                    self.data[k][l] = self.op(self.data[k][2*l], self.data[k][2*l+1])
            for k in range(1,self.N0)[::-1]:
                for l in range(self.M0+M)[::-1]:
                    self.data[k][l] = self.op(self.data[2*k][l], self.data[2*k+1][l])

    # a_k の値を x に更新
    def update(self,i,j,x):
        self.data[i+self.N0][j+self.M0] = x
        data_ii = self.data[i+self.N0]
        jj = (j+self.M0)>>1
        while jj:
            data_ii[jj] = self.op(data_ii[2*jj], data_ii[2*jj+1])
            jj >>= 1
        ii = (i+self.N0)>>1
        while ii:
            jj = j+self.M0
            while jj:
                self.data[ii][jj] = self.op(self.data[2*ii][jj], self.data[2*ii+1][jj])
                jj >>= 1
            ii >>= 1
    
    # 区間[L1,R1)*[L2,R2)をopでまとめる
    def prod(self,L1,R1,L2,R2):
        L1 += self.N0; R1 += self.N0
        L2 += self.M0; R2 += self.M0
        sl = sr = self.e
        while L1 < R1:
            if R1 & 1:
                R1 -= 1
                sr = self.op(self._prod_fixed(R1,L2,R2),sr)
            if L1 & 1:
                sl = self.op(sl,self._prod_fixed(L1,L2,R2))
                L1 += 1
            L1 >>= 1; R1 >>= 1
        return self.op(sl,sr)

    # 区間 seg[i]*[L-self.M0,R2-self.M0)をopでまとめる
    def _prod_fixed(self,i,L,R):
        sl = sr = self.e
        data_i = self.data[i]
        while L < R:
            if R & 1:
                R -= 1
                sr = self.op(data_i[R],sr)
            if L & 1:
                sl = self.op(sl,data_i[L])
                L += 1
            L >>= 1; R >>= 1
        return self.op(sl,sr)

    def all_prod(self):
        return self.data[1][1]

    def get(self, i,j): #k番目の値を取得。
        return self.data[i+self.N0][j+self.M0]
