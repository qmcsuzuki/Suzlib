# competitive-verifier: TITLE 隣り合う値が異なるように並べ替える
def rearrange_without_adjacent_equal(seq):
    """
    seq を並べ替えて、隣接する 2 要素が異なるようにできるかを判定・構築
    返り値: List （不可能なら空リスト）
    """
    n = len(seq)
    if n == 1: return seq[:]

    cnt = {}
    for x in seq:
        cnt[x] = cnt.get(x, 0) + 1

    max_x = seq[0]
    max_c = -1
    for x, c in cnt.items():
        if c > max_c:
            max_x = x
            max_c = c

    if max_c > (n + 1) // 2:
        return []

    ans = [seq[0]]*n
    pos = 0

    for _ in range(max_c):
        ans[pos] = max_x
        pos += 2

    for x, c in cnt.items():
        if x == max_x:
            continue
        for _ in range(c):
            if pos >= n:
                pos = 1
            ans[pos] = x
            pos += 2

    return ans
