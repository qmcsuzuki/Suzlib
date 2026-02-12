# competitive-verifier: TITLE 根付き木のハッシュ


"""
根付き木の各部分木の完全ハッシュ関数を求める（同型が判定できる）
"""
def rooted_tree_hash(g,root,par=None,dfs_order=None):
    n = len(g)
    if par is None or dfs_order is None:
        st = [root]
        par = [-1]*n
        dfs_order = []
        while st:
            dfs_order.append(v := st.pop())
            for c in g[v]:
                if v == par[c]: continue
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

