"""
Cartesian tree を構築。最小値で列を分割する（同じ値は左を優先的に使う）
以下の三つの関数がある

- Cartesian_tree_DFSsearch(A,calc):
    - calc(i,l,r,p) を DFS 順に行う
- Cartesian_tree_full(A): Cartesian tree の情報を返す
- Cartesian_tree_simple(A): シンプルに親だけを返す
"""

def Cartesian_tree_DFSsearch(A, calc):
    if not A: return # avoid empty list
    n = len(A)
    A.append(min(A)-1) # 番兵
    L = [-1]*(n+1)
    for i,ai in enumerate(A):
        cur = i-1
        while cur != -1 and A[cur] > ai:
            l = L[cur]+1
            r = i
            p = l-1 if (r == n or (l != 0 and A[l-1] > A[r])) else r
            """
            cur が管理する半開区間 [l:r] および親 p 確定（両端のうち大きい値が親）
            ここで cur に関する計算を行う
            """
            calc(cur,l,r,p)

            cur = l-1
        L[i] = cur
    A.pop()


"""
頂点 i の親は P[i] で、開区間 (L[i],R[i]) を管理する、という情報を返す
"""
def Cartesian_tree_full(A):
    n = len(A)
    L = [-1]*n # vertex i cover open interval (L[i], R[i])
    R = [n]*n 
    P = [-1]*n # parent of Cartesian tree
    for i,Ai in enumerate(A):
        cur = i-1
        pre = -1
        while cur != -1 and A[cur] > Ai:
            R[cur] = i
            cur, pre = L[cur], cur
        L[i] = P[i] = cur
        if pre != -1:
            P[pre] = i
    return L,R,P


# 親だけを返すシンプルな Cartesian tree
def Cartesian_tree_simple(A):
    par = [-1]*len(A)
    for i,Ai in enumerate(A):
        cur = i-1
        pre = -1
        while cur != -1 and A[cur] > Ai:
            cur, pre = par[cur], cur
        par[i] = cur
        if pre != -1:
            par[pre] = i
    return par
