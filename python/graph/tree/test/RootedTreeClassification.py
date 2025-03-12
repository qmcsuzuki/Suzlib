# verification-helper: PROBLEM https://judge.yosupo.jp/problem/rooted_tree_isomorphism_classification

from python.graph.tree.RootedTreeHash import rooted_tree_hash

import sys
readline = sys.stdin.readline

n = int(readline())
*p, = map(int,readline().split())
p.insert(0,-1) # par

g = [[] for _ in range(n)]
for i in range(1,n):
    g[p[i]].append(i)
    g[i].append(p[i])
ans = rooted_tree_classification(g,0,par=p,dfs_order=list(range(n)))

print(max(ans)+1)
print(*ans)

# https://judge.yosupo.jp/submission/272729
