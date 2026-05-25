# competitive-verifier: TITLE 区間加算・区間内積 mod 998244353


class RangeAddRangeInnerproductMOD(LazySegmentTree):
    """
    数列 A,B に区間加算、A と B の区間内積
    
    lazy: (p,q) の 1 次元化
    data: ((sum(ai*bi),sum(wi))の 1 次元化, (sum(ai),sum(bi)) の 1 次元化)
    """
    MOD = 998244353
    M = 1<<30

    def __init__(self,N,A=None,B=None,W=None):
        self.e_X = (0,0); self.id_M = 0
        self.N = N
        self.log = (N-1).bit_length()
        self.N0 = 1<<self.log
        self.data = [self.e_X]*(2*self.N0)
        self.lazy = [self.id_M]*self.N0

        if W is None:
            W = [1]*N
        if A is not None:
            assert len(A)==N
            array = [(A[i]*B[i]%self.MOD*self.M + W[i]%self.MOD,  A[i]%self.MOD*self.M + B[i]%self.MOD) for i in range(N)]
        else:
            array = [(W[i]%self.MOD,0)]

        self.data[self.N0:self.N0+self.N] = array
        for i in range(self.N0-1,0,-1): self.update(i)

    def op_X(self,X,Y):
        rx,wx = divmod(X[0],self.M)
        ax,bx = divmod(X[1],self.M)
        ry,wy = divmod(Y[0],self.M)
        ay,by = divmod(Y[1],self.M)
        rw = (rx+ry)%self.MOD*self.M + (wx+wy)%self.MOD
        ab = (ax+ay)%self.MOD*self.M + (bx+by)%self.MOD
        return (rw,ab)

    def mapping(self,xy,X):
        r,w = divmod(X[0],self.M)
        a,b = divmod(X[1],self.M)
        p,q = divmod(xy,self.M)
        r = (r + q*a + p*b + p*q%self.MOD*w)%self.MOD
        a = (a+w*p)%self.MOD
        b = (b+w*q)%self.MOD
        return (r*self.M+w, a*self.M+b)

    def compose(self,X,Y):
        x0,x1 = divmod(X,self.M)
        y0,y1 = divmod(Y,self.M)
        return (x0+y0)%self.MOD*self.M + (x1+y1)%self.MOD
