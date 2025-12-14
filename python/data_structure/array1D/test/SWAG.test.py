# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/queue_operate_all_composite

from python.data_structure.array1D.SlidingWindowAggregation import SWAG

import sys
readline = sys.stdin.readline

def merge(a,b):
    return (a[0]*b[0]%MOD,(b[0]*a[1]+b[1])%MOD)
swag = SWAG(merge,(1,0))

MOD = 998244353
q = int(input())
for _ in range(q):
    a = [int(i) for i in input().split()]
    if a[0]==0:
        swag.append((a[1],a[2]))
    elif a[0]==1:
        swag.popleft()
    else:
        p,q = swag.fold_all()
        print((p*a[1]+q)%MOD)

