# competitive-verifier: TITLE Suffix Array Doubling

"""
- suffix_array_functional_graph(nexts,labels): 一般の functional graph で suffix array の一般化
- suffix_array_doubling(S): 普通の文字列や数列 S のダブリング
"""

def suffix_array_functional_graph(nexts: list[int], labels: list[int]) -> tuple[list[int], list[int]]:
    """
    functional graph 上の「無限ラベル列」を辞書順にソートした順序（suffix array 相当）を返す。
    doubling で suffix array を求めるやつ
    
    引数:
    - nexts[v]  : f(v)（0 <= nexts[v] < N）
    - labels[v] : 辺 v -> nexts[v] に付いたラベル（整数）

    返り値:
    - sa   : list[int]
        無限列の辞書順で昇順ソートされた頂点番号の配列。
    - rank : list[int]
        rank[v] は v の順位（0..R-1）。rank が等しい頂点同士は無限列が完全に一致する。
    """
    n = len(nexts)
    if n == 0:
        return [], []
    assert len(labels) == n

    # 初期状態でのラベルのランク付け
    mx = max(labels)
    if min(labels) >= 0 and mx < 1000:
        rank = list(labels)
        R = mx + 1
    else: # 座圧
        uniq = sorted(set(labels))
        comp = {a: i for i, a in enumerate(uniq)}
        rank = [comp[a] for a in labels]
        R = len(uniq)

    order: list[int] = list(range(n))  # will be kept sorted by current keys
    nxt: list[int] = list(nexts)        # nxt[v] = f^{L}(v)
    L = 1

    def counting_sort(order: list[int], key: list[int], R: int) -> list[int]:
        # key[v] in [0, R) で、order をカウントソート
        cnt = [0] * R
        for v in order:
            cnt[key[v]] += 1
        s = 0
        for i in range(R):
            cnt[i], s = s, s + cnt[i]
        out = [0] * len(order)
        for v in order:
            out[cnt[key[v]]] = v
            cnt[key[v]] += 1
        return out

    while L < n:
        key1 = rank
        key2 = [rank[nxt[v]] for v in range(n)]
        order = counting_sort(order, key2, R)
        order = counting_sort(order, key1, R)

        # re-rank
        new_rank = [0] * n
        r = 0
        pv = order[0]
        new_rank[pv] = 0
        for v in order[1:]:
            if key1[v] != key1[pv] or key2[v] != key2[pv]:
                r += 1
                pv = v
            new_rank[v] = r
        rank = new_rank
        R = r + 1

        # update nxt to f^{2L}
        nxt = [nxt[nxt[v]] for v in range(n)]
        L <<= 1

    sa = order
    return sa, rank


def suffix_array_doubling(S) -> list[int]:
    """
    S (str or list[int]) の suffix array（0-index, 長さ n）を返す（doubling + counting sort）。
    """
    if isinstance(S, str):
        a: list[int] = [ord(c) + 1 for c in S]
    else:
        if len(S) == 0:
            return []
        mn = min(S)
        a: list[int] = [v - mn + 1 for v in S]

    n = len(a)
    a.append(0)
    nexts: list[int] = list(range(1, n+1)) + [n]

    sa, _ = suffix_array_functional_graph(nexts, a)
    return [i for i in sa if i < n] # 終端（頂点 n）に相当するものを除外
