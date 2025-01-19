class Accumulate2dim:
    """
    a: h*w 行列
    acc: a の累積和（原点スタート、番兵の 0 を入れる）
        i.e. acc[x][y] = sum(a[i][j] for i in range(x) for j in range(y)]
    """
    def __init__(self,a):
        self.h = len(a); self.w = len(a[0])
        h,w = self.h + 1, self.w +1
        self.acc = acc = [0]*(h*w)
        for i in range(1,h):
            for j in range(1,w):
                acc[i*w+j] = a[i-1][j-1] + acc[i*w+j-1] \
                            + acc[i*w+j-w] - acc[i*w+j-w-1]

    def prefix_sum(self,h,w):
        #半開長方形 [0,h2)*[0,w2) の和
        assert 0 <= h and 0 <= w
        return self.acc[h*(1+self.w) + w]

    def range_sum(self,h1,h2,w1,w2):
        #半開長方形 [h1,h2)*[w1,w2) の和
        assert 0 <= h1 <= h2 and 0 <= w1 <= w2
        return (self.acc[h1*(1+self.w) + w1]
                    - self.acc[h1*(1+self.w) + w2]
                    - self.acc[h2*(1+self.w) + w1]
                    + self.acc[h2*(1+self.w) + w2]
                )

    def prefix_sum_large(self,x,y):
        # h*w のパターンが無限に繰り返されている場合の半開長方形 [0,x)*[0,y) の和
        assert 0 <= x and 0 <= y
        xq,xr = divmod(x,self.h)
        yq,yr = divmod(y,self.w)
        return (self.prefix_sum(self.h,self.w)*xq*yq
            + self.prefix_sum(xr,self.w)*yq
            + self.prefix_sum(self.h,yr)*xq
            + self.prefix_sum(xr,yr))

    def range_sum_large(self,h1,h2,w1,w2):
        # h*w のパターンが無限に繰り返されている場合の半開長方形 [h1,h2)*[w1,w2) の和
        assert 0 <= h1 <= h2 and 0 <= w1 <= w2
        return (self.prefix_sum_large(h1,w1)
            - self.prefix_sum_large(h1,w2)
            - self.prefix_sum_large(h2,w1)
            + self.prefix_sum_large(h2,w2))

##############################################################
# https://atcoder.jp/contests/abc331/submissions/61878084
##############################################################
