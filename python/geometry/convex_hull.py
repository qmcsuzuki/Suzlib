"""
凸包の頂点indexを時計回り（右回り）に列挙する
同一直線上の頂点は、ムダな点を消して端のみ残す（そうしないことも可能）
points をソートするという副作用がある点に注意
"""
def convex_hull(points,need_sort=True):
    def cross(i,j,k):
        """
        ベクトル ij と ベクトル ik の内積（正なら班時計周り）
        """
        xi,yi = points[i]
        xj,yj = points[j]
        xk,yk = points[k]
        return (xj-xi)*(yk-yj) - (yj-yi)*(xk-xj) 

    n = len(points)
    if need_sort: points.sort()
    lst = []
    for i in range(n):
        while len(lst) > 1 and cross(lst[-2],lst[-1],i) >= 0: #この式と下式の不等号のイコールをはずすと同一直線上を許す（凸包が退化する場合に注意）
            lst.pop()
        lst.append(i)
    t = len(lst)
    for i in range(n-1)[::-1]:
        while len(lst) > t and cross(lst[-2],lst[-1],i) >= 0:
            lst.pop()
        lst.append(i)
    return lst[:-1]

##########################################################################
# https://judge.u-aizu.ac.jp/onlinejudge/review.jsp?rid=5498674
##########################################################################

import sys
readline = sys.stdin.readline

n = int(input())
yx = []
for _ in range(n):
    x,y = map(int,input().split())
    yx.append((y,x))
lst = convex_hull(yx)
print(len(lst))
for i in lst:
    y,x = yx[i]
    print(x,y)
