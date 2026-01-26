# competitive-verifier: TITLE 転倒数、隣接 swap 回数

"""
数列 A の転倒数を求める
仮定: 0 <= ai <= n
（順列なら 0-indexed, 1-indexed 両対応）
"""
def inversion(a):
    n = len(a)+1
    data = [0]*(n+1)
    v = (n-1)*(n-2)//2
    for ai in a:
        # bit.sum
        i = ai + 1
        while i > 0:
            v -= data[i]
            i -= i & -i
        # bit.add
        i = ai + 1
        while i <= n:
            data[i] += 1
            i += i & -i
    return v

"""
数列 A,B は隣接swap何回で移りあうか？
移りあえないなら -1
"""
def inversion_distance(A,B):
    from collections import defaultdict
    d = defaultdict(list)
    for i,bi in enumerate(B):
        d[bi].append(i)
    
    res = [0]*n # A[i] mapsto B[res[i]]
    for i in range(len(A))[::-1]:
        try:
            res[i] = d[A[i]].pop()
        except IndexError:
            return -1
    return inversion(res)

# 愚直 O(N^2)
def inversion_brute(A):
    cnt = 0
    for i in range(1,len(A)):
        for j in range(i):
            if A[j] > A[i]:
                cnt += 1
    return cnt

# 愚直、A,B は 0~L-1 の順列を仮定
def inversion_distance_brute(A,B):
    L = len(A)
    assert L == len(B) and min(A) == 0
    res = [0]*L
    for i in range(L):
        res[A[i]] = i
    return inbersion_brute([res[v] for v in B])
