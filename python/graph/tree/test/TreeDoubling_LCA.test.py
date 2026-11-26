# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/lca

from sys import stdin
from python.graph.tree.TreeDoubling import TreeDoubling


if __name__ == "__main__":
    input = stdin.readline
    n, q = map(int, input().split())
    g = [[] for _ in range(n)]
    for v, p in enumerate(map(int, input().split()), 1):
        g[p].append(v)
    D = TreeDoubling(g)
    ans = []
    for _ in range(q):
        u, v = map(int, input().split())
        ans.append(str(D.lca(u, v)))
    print("\n".join(ans))
