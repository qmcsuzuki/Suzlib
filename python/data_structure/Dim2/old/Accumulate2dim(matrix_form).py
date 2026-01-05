# verification-helper: TITLE 2次元累積和（行列形式）

class Accumulate2dim:
    """
    a: h*w 行列
    acc: a の累積和（原点スタート、番兵の 0 を入れる）
        i.e. acc[x][y] = sum(a[i][j] for i in range(x) for j in range(y)]
    """
    def __init__(self,a):
        self.h = h = len(a); self.w = w = len(a[0])
        self.acc = acc = [[0]*(w+1) for _ in range((h+1))]
        for i in range(1,h+1):
            for j in range(1,w+1):
                acc[i][j] = a[i-1][j-1] + acc[i][j-1] - acc[i-1][j-1] + acc[i-1][j]

    def get_sum_from_origin(self,h,w):
        #半開長方形 [0,h2)*[0,w2) の和
        assert 0 <= h and 0 <= w
        return self.acc[h][w]

    def get_sum(self,h1,h2,w1,w2):
        #半開長方形 [h1,h2)*[w1,w2) の和
        assert 0 <= h1 <= h2 and 0 <= w1 <= w2
        return self.acc[h1][w1] - self.acc[h1][w2]  - self.acc[h2][w1] + self.acc[h2][w2]

    def get_sum_from_origin_large(self,x,y):
        # h*w のパターンが無限に繰り返されている場合の半開長方形 [0,x)*[0,y) の和
        assert 0 <= x and 0 <= y
        xq,xr = divmod(x,self.h)
        yq,yr = divmod(y,self.w)
        return (self.get_sum_from_origin(self.h,self.w)*xq*yq
            + self.get_sum_from_origin(xr,self.w)*yq
            + self.get_sum_from_origin(self.h,yr)*xq
            + self.get_sum_from_origin(xr,yr))

    def get_sum_large(self,h1,h2,w1,w2):
        # h*w のパターンが無限に繰り返されている場合の半開長方形 [h1,h2)*[w1,w2) の和
        assert 0 <= h1 <= h2 and 0 <= w1 <= w2
        return (self.get_sum_from_origin_large(h1,w1)
            - self.get_sum_from_origin_large(h1,w2)
            - self.get_sum_from_origin_large(h2,w1)
            + self.get_sum_from_origin_large(h2,w2))

##############################################################
# https://atcoder.jp/contests/abc331/submissions/61750409
##############################################################

import sys
readline = sys.stdin.readline

#n = int(readline())
#*a, = map(int,readline().split())

n,Q = map(int,readline().split())
board = [[1 if i=="B" else 0 for i in readline().strip()] for _ in range(n)]

seg = Accumulate2dim(board)

def f(x,y):
    if x < 0 or y < 0: return 0
    x += 1
    y += 1

    xq,xr = divmod(x,n)
    yq,yr = divmod(y,n)
    ans = seg.get_sum(0,n,0,n)*xq*yq
    ans += seg.get_sum(0,xr,0,n)*yq
    ans += seg.get_sum(0,n,0,yr)*xq
    ans += seg.get_sum(0,xr,0,yr)
    
    res = seg.get_sum_from_origin(n,n)*xq*yq
    res += seg.get_sum_from_origin(xr,n)*yq
    res += seg.get_sum_from_origin(n,yr)*xq
    res += seg.get_sum_from_origin(xr,yr)
    assert ans == res
    
    return ans


for _ in range(Q):
    a,b,c,d = map(int,readline().split())
    ans1 = seg.get_sum_large(a,c+1,b,d+1)
    ans2 = f(c,d) - f(a-1,d) - f(c,b-1) + f(a-1,b-1)
    assert ans1 == ans2
    print(ans1)

