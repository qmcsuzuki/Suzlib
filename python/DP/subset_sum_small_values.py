# competitive-verifier: TITLE 小さい値の部分和
"""
subset sum を O(N max A) で解く (Pisinger)
A: 値のリスト
C: 和の上限
return:
  - ans: 部分和の最大値
  - res2: 各要素を選んだかどうかを表す 0/1 リスト（元の A の順）
"""
def subset_sum(A,C):
    assert C >= 0
    if sum(A) <= C:
        return (sum(A), [1]*len(A))

    # 定数倍がよくなることを期待してソートしておく
    order = sorted(range(len(A)), key = lambda i:A[i])
    A = sorted(A)
    if A[0] > C: return (0,[0]*len(A))

    r = 0
    for i,ai in enumerate(A):
        if r + ai > C:
            break
        r += ai
    maxA = max(A)
    b = i # [0:b], [b:n] で balancing
    # C-W+1 <= v <= C+W のみ管理
    # dp[t][v] = max(s: 閉区間 [s,t] のみを変更する balancing で v を作れる)
    offset = C-maxA+1
    old = [-1]*maxA + [0]*maxA
    dp = old[:]
    dp[r-offset] = b
    prev_index = []
    for t in range(b,len(A)):
        prev = [-1]*(2*maxA)
        for i in range(maxA)[::-1]:
            if dp[i+A[t]] < dp[i]:
                dp[i+A[t]] = dp[i]
                prev[i+A[t]] = t
        for i in range(maxA,2*maxA)[::-1]:
            for j in range(old[i],dp[i]):
                if dp[i-A[j]] < j:
                    dp[i-A[j]] = prev[i-A[j]] = j
            old[i] = dp[i]
        prev_index.append(prev)
    # 最大解の復元
    for v in range(maxA)[::-1]:
        if dp[v] != -1: break
    ans = v + offset
    res = [1]*b + [0]*(len(A)-b)
    for prev in prev_index[::-1]:
        idx = prev[v]
        while 0 <= idx < b:
            v += A[idx]
            res[idx] ^= 1
            idx = prev[v]
        if idx != -1:
            v -= A[idx]
            res[idx] ^= 1
    
    res2 = [0]*len(A)
    for i,ri in enumerate(res):
        res2[order[i]] = ri
    return (ans,res2)
