# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/jump_on_tree

from sys import stdin
from python.graph.tree.TreeDoubling import TreeDoubling


if __name__ == "__main__":
    input = stdin.readline
    n, q = map(int, input().split())
    g = [[] for _ in range(n)]
    for _ in range(n-1):
        u, v = map(int, input().split())
        g[u].append(v)
        g[v].append(u)
    D = TreeDoubling(g)
    depth = D.depth
    ans = []
    for _ in range(q):
        s, t, k = map(int, input().split())
        a = D.lca(s, t)
        ds = depth[s] - depth[a]
        dt = depth[t] - depth[a]
        if k > ds + dt:
            v = -1
        elif k <= ds:
            v = D.kth_pos(k, s)
        else:
            v = D.kth_pos(ds + dt - k, t)
        ans.append(str(v))
    print("\n".join(ans))
