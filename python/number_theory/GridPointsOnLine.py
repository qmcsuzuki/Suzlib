# verification-helper: TITLE 格子点の直線上個数

def count_integer_points_of_queen_moves(a,b,c,x_min,x_max,y_min,y_max):
    # find number of (ax + by = c, x_min <= x < x_max, y_min <= y < y_max)
    # 範囲が range のように半開区間になっている点に注意
    # ここで (a,b) は 8 方向を表す （つまり {-1,0,1}^2 から (0,0) を除いたもの）
    if a == 0:
        assert b != 0
        return x_max-x_min if y_min <= c < y_max else 0
    elif b == 0:
        return y_max-y_min if x_min <= c//a < x_max else 0
    if a == -1:
        a = 1; b = -b; c = -c
    if b == 1: # y -> -y 置換
        b = -1; y_min, y_max = -y_max+1, -y_min+1
    assert a == 1 and b == -1
    return max(0, min(x_max,c+y_max)-max(x_min,c+y_min))

# https://atcoder.jp/contests/abc377/submissions/62326704

def grid_points_on_line(a,b,c,x_min,x_max,y_min,y_max):
    """
    consider (ax + by = c, x_min <= x <= x_max, y_min <= y <= y_max)
    return (L,R,x0,y0) where set is [(x0+t*b,y_0-t*a) for t in range(L,R)]
    (if no solution, then return 0,0,x0,y0)
    The number of solution is R-L
    """    
    assert b != 0
    if a == 0:
        if c%b: return 0,0,0,0
        if y_min <= c//b <= y_max:
            return x_min,x_max+1,0,c//b
        else:
            return 0,0,0,0
    if b < 0: a,b,c = -a,-b,-c

    x0,y0,g = extgcd(a,b)
    if c%g: return 0,0,0,0
    x0 *= c//g
    y0 *= c//g
    a //= g
    b //= g
    L = max((x_min-x0+b-1)//b, (y0-y_max+a-1)//a if a>0 else (y_min-y0-a-1)//(-a))
    R = min((x_max-x0)//b, (y0-y_min)//a if a>0 else (y_max-y0)//(-a))
    if L > R: return 0,0,x0,y0
    return L,R+1,x0,y0


#################

def brute(a,b,c,L,n,R,m):
    cnt = 0
    for x in range(L,n+1):
        for y in range(R,m+1):
            if a*x+b*y==c: cnt += 1
    return cnt

def test():
    from itertools import product
    n,m = 8,10
    for a,b,c in product(range(-5,5),repeat=3):
        if b == 0: continue
        for L,R in product(range(-3,3),repeat=2):
            res1 = grid_points_on_line(a,b,c,L,n,R,m)
            res2 = brute(a,b,c,L,n,R,m)
            if res1[1]-res1[0]!=res2:
                print(res1,res1[1]-res1[0],res2,"data: ",a,b,c,L,n,R,m)
                assert 0

test()

# https://atcoder.jp/contests/abc315/submissions/62342029
