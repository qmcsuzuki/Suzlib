# competitive-verifier: TITLE Floor Sum

from python.math.number_theory.extgcd import extgcd

"""
sum((a*i+b)//m for i in range(n)) を返す
a,b <= 0 もOK
O(log(n+m+a+b))
"""
def floor_sum(n,m,a,b):
    res = 0
    while True:
        res += (n-1)*n//2*(a//m) + (b//m)*n
        a %= m
        b %= m
        if a*n+b <= m:
            return res
        n,b = divmod(a*n+b,m)
        m,a = a,m

"""
ax + by <= t, x >= 0, y >= 0 をみたす x,y の個数
辺上も含むことに注意
"""
def points_in_triange(a,b,t):
    return floor_sum(1+t//a,b,a,t%a) + t//a + 1

"""
ax + by = t, x >= 0, y >= 0 をみたす x,y の個数
"""
def points_on_line(a,b,t):
    g,p,q = extgcd(a,b)
    return 0 if t%g else t*q//a + t*p//b + 1


