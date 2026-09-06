# competitive-verifier: TITLE 強連結成分分解 (SCC)


def find_SCC(g):
    """
    グラフ g の SCC、各頂点の SCC 番号、縮約 DAG を返す。
    SCC 番号はトポロジカル順で、縮約 DAG の多重辺は除く。
    Gabow の path-based SCC algorithm を用いる。
    """
    n = len(g)

    SCC = []
    S = []  # Gabow の active stack
    P = []  # Gabow の root stack。S 上の根候補の位置を持つ
    pos = [0] * n  # 0: 未訪問, >0: S 上での位置, -1: SCC 確定済み
    comp = [-1] * n

    for i in range(n):
        if comp[i] != -1:
            continue

        st = [i]
        while st:
            v = st.pop()

            if v < 0:  # 帰りがけ
                v = ~v
                d = pos[v] - 1
                if P[-1] > d:  # v が根候補として残っている
                    SCC.append(S[d:])
                    P.pop()
                    del S[d:]

                    c = len(SCC) - 1
                    for u in SCC[-1]:
                        pos[u] = -1
                        comp[u] = c

            elif pos[v] > 0:  # SCC 未確定の頂点への辺
                while P[-1] > pos[v]:
                    P.pop()

            elif pos[v] == 0:  # 初訪問
                S.append(v)
                P.append(len(S))
                pos[v] = len(S)
                st.append(~v)
                st += g[v]

    k = len(SCC)
    groups = SCC[::-1]
    comp = [k - 1 - c for c in comp]

    return groups, comp, condensation_graph(g, groups, comp)


def condensation_graph(g, groups, comp):
    """
    SCC を縮約し、多重辺を除いた DAG の隣接リストを返す。
    """
    k = len(groups)
    dag = [[] for _ in range(k)]
    seen = [-1] * k  # seen[d] == c: SCC c から d への辺を追加済み

    for c, vs in enumerate(groups):
        for u in vs:
            for v in g[u]:
                d = comp[v]
                if d != c and seen[d] != c:
                    seen[d] = c
                    dag[c].append(d)

    return dag
