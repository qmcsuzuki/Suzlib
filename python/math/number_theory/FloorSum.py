# competitive-verifier: TITLE Floor Sum

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



"""
test code

def bruteforce(n,m,a,b):
    return sum((a*i+b)//m for i in range(n)) 

def test(N):
    for a in range(-N,N):
        for b in range(-N,N):
            for m in range(1,N):
                for n in range(N):
                    x = floor_sum(n,m,a,b)
                    y = bruteforce(n,m,a,b)
                    if x != y:
                        print(a,b,m,n)
                        assert x == y

    print(f"test:passed, N={N}")
"""

#############################################
# https://atcoder.jp/contests/practice2/submissions/16599032
#############################################
        
import sys
readline = sys.stdin.buffer.readline
read = sys.stdin.read

T = int(readline())
for _ in range(T):
    n,m,a,b = map(int,readline().split())
    print(floor_sum(n,m,a,b))
