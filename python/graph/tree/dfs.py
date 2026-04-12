# competitive-verifier: TITLE 深さ優先探索 (DFS)

"""
木の入力と DFS の基本情報を作る補助関数群。
"""


def input_tree(n, offset=1):
    """
    木を入力して隣接リストを返す。

    引数:
    - n: 頂点数
    - offset: 入力頂点番号の基準（1-indexed なら 1, 0-indexed なら 0）

    返り値:
    - g: 隣接リスト

    計算量: O(n)
    """
    g = [[] for _ in range(n)]
    for _ in range(n - 1):
        u, v = map(int, readline().split())
        u -= offset
        v -= offset
        g[u].append(v)
        g[v].append(u)
    return g


def get_order_and_parent(g, root):
    """
    root から DFS した訪問順と親配列を返す。

    引数:
    - g: 木の隣接リスト
    - root: 根頂点

    返り値:
    - order: DFS の訪問順
    - par: 親配列（par[root] = -1）

    計算量: O(n)
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


def get_size(order, par):
    """
    DFS 順と親配列から部分木サイズを返す。

    引数:
    - order: DFS の訪問順
    - par: 親配列

    返り値:
    - size: 部分木サイズ配列

    計算量: O(n)
    """
    n = len(par)
    size = [1] * n
    for v in order[::-1]:
        if par[v] != -1:
            size[par[v]] += size[v]
    return size
