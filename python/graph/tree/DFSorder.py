# competitive-verifier: TITLE DFS順序（オイラーツアー）

"""
return
- order[i]: i 番目の頂点
- ls[v]: 頂点 v の位置（DFS order で何番目か）（order, ls は互いに逆配列）
- size[v]: 部分木 v のサイズ

頂点 v の部分木: 半開区間 [ls[v]:ls[v]+size[v]]

"""
def DFSorder(g,root):
    n = len(g)
    par = [-1]*n
    ls = [0]*n
    size = [1]*n
    q = [root]
    order = []
    for clock in range(n):
        v = q.pop()
        order.append(v)
        ls[v] = clock
        for c in g[v][::-1]:
            if c != par[v]:
                par[c] = v
                q.append(c)
    
    for i in order[1:][::-1]:
        size[par[i]] += size[i]
        
    return order,ls,size

# n = int(readline())
# g = [[] for _ in range(n)]

# for _ in range(n-1):
#     u,v = map(int,readline().split())
#     u -= 1
#     v -= 1
#     g[u].append(v)
#     g[v].append(u)

# https://atcoder.jp/contests/abc406/submissions/66390791
