# competitive-verifier: TITLE DFSで情報を持ち回る

"""貼り付け用の無向木 DFS テンプレート。n と隣接リスト g を先に定義する。
根は 0、st の非負の頂点は行きがけ、~v は帰りがけを表す。"""

par = [-1]*n
st = [~0,0]
val = [0]*n
while st:
    v = st.pop()
    if v >= 0: #行きがけ
        # ここで行きがけ処理
        #
        #
        # ここまで行きがけ処理
        for u in g[v]:
            if u == par[v]: continue
            par[u] = v
            st.append(~u)
            st.append(u)
    else: #帰りがけ
        v = ~v
        # ここで帰りがけ処理
        #
        # ここまで帰りがけ処理
