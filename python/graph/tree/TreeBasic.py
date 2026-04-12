# competitive-verifier: TITLE 木の基本関数（DFS順、親、サイズ、深さ）

""" usage
g = input_tree(n, offseet=1)
order, par = get_order_and_parent(g, root=0)
size = getsize(g,wt=None) # 重み 1
depth = get_depth(order, par)
"""


# 木を入力して隣接リストを返す。
def input_tree(n, offset=1):
    """
    引数:
    - n: 頂点数
    - offset: 入力頂点番号の基準（1-indexed なら 1, 0-indexed なら 0）

    返り値:
    - g: 隣接リスト
    """
    g = [[] for _ in range(n)]
    for _ in range(n-1):
        u, v = [int(i)-offset for i in readline().split()]
        g[u].append(v)
        g[v].append(u)
    return g


# root から DFS した訪問順と親配列を返す。
def get_order_and_parent(g, root):
    """
    返り値:
    - order: DFS の訪問順
    - par: 親配列（par[root] = -1）
    """
    n = len(g)
    par = [-1] * n
    order = []
    st = [root]
    while st:
        v = st.pop()
        order.append(v)
        for c in g[v]:
            if c != par[v]:
                par[c] = v
                st.append(c)
    return order, par

# 部分木サイズ（または部分木重み和）を返す
def get_size(order, par, wt=None):
    """
    引数:
    - order: DFS の訪問順
    - par: 親配列
    - wt: 各頂点の重み配列。None のときは全頂点の重みを 1 とみなす

    返り値:
    - size: 部分木サイズ配列（wt 指定時は部分木重み和）
    """
    n = len(par)
    size = [1] * n if wt is None else wt[:]
    for v in order[::-1]:
        if par[v] != -1:
            size[par[v]] += size[v]
    return size

#DFS 順と親配列から各頂点の深さを返す
def get_depth(order, par): 
    # 返り値: depth: 深さ配列（根は order[0]）
    depth = [0] * len(par)
    for v in order:
        p = par[v]
        if p != -1:
            depth[v] = depth[p] + 1
    return depth
