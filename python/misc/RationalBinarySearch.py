# competitive-verifier: TITLE 有理数二分探索

"""
Stern-Brocot 木上で単調な check を二分探索する。
check(0,1) = False, check(1,0) = True を仮定する。
is_valid(p,q) は探索可能な分数 p/q なら True を返す。
返り値 (a,b,c,d) は境界を挟む a/b, c/d。
"""
def RationalBinarySearch(check, is_valid):
    assert check(1,0) and not check(0,1)

    a,b,c,d,p,q = 0,1,1,0,1,1

    while is_valid(p,q):
        D = 1
        t = 0
        is_mid_OK = check(p,q)
        x,y = (a,b) if is_mid_OK else (c,d)

        while is_valid(x*D+p, y*D+q) and check(x*D+p, y*D+q) == is_mid_OK:
            D <<= 1

        while D > 1:
            D >>= 1
            if is_valid(x*(t+D)+p, y*(t+D)+q) and check(x*(t+D)+p, y*(t+D)+q) == is_mid_OK:
                t += D

        if is_mid_OK:
            c,d = x*t+p, y*t+q
        else:
            a,b = x*t+p, y*t+q

        p,q = a+c, b+d

    return a,b,c,d
