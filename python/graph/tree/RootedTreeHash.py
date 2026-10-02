# competitive-verifier: TITLE 根付き木のハッシュ


"""
根付き木の各部分木を同型類の整数 ID に分類する。
ID の一致が同型を意味するのは同じ呼び出し内だけで、別々の木で得た ID は比較できない。
par と dfs_order を省略すると root から構築する。指定時は親が子より先の訪問順を渡す。
時間 O(N log N)、空間 O(N)。子リストの整列により衝突なく分類する。
"""
def rooted_tree_hash(g,root,par=None,dfs_order=None):
    """指定した根に関する各部分木を、同型なものが同じ番号になるよう分類する。"""
    n = len(g)
    if par is None or dfs_order is None:
        st = [root]
        par = [-1]*n
        dfs_order = []
        while st:
            dfs_order.append(v := st.pop())
            for c in g[v]:
                if c == par[v]: continue
                st.append(c)
                par[c] = v

    hashing = lambda v,lst: tuple(sorted(lst)) # 別のハッシュに置き換え可能
    hash_to_ID = dict()
        
    ID = [-1]*n
    idx = 0
    for v in dfs_order[::-1]:
        h = hashing(v,[ID[c] for c in g[v] if c != par[v]])
        if h in hash_to_ID:
            ID[v] = hash_to_ID[h]
        else:
            ID[v] = hash_to_ID[h] = idx
            idx += 1    
    return ID

