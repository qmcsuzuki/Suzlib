n = int(readline())

g = [[] for _ in range(n)]
for _ in range(n):
    u,v = map(int,readline().split())
    u -= 1
    v -= 1
    g[u].append(v)
    g[v].append(u)

order = []
st = [0]
parent = [-1]*n
#depth = [0]*n
while st:
    v = st.pop()
    order.append(v)
    for c in g[v]:
        if c != parent[v]:
            st.append(c)
            parent[c] = v
            #depth[c] = depth[v] + 1

size = [1]*n
for i in order[::-1]:
    if i==root: break
    size[parent[i]] += size[i]
