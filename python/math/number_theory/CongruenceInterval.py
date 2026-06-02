# competitive-verifier: TITLE 区間内で n=a mod M をみたす n の個数、最小、最大

def residue_range(L: int, R: int, r: int, m: int) -> tuple[int, int, int]:
    """
    x in range(L, R) かつ x == r mod m となるような（つまり半開区間 [L,R) 上で余り r になる x）
    (x の個数, 最小の x, 最大の x) を返す。

    存在しない場合、count = 0 であり、x_min, x_max は意味を持たない。
    """
    assert m > 0
    r %= m

    x_min = L + (r - L) % m
    x_max = R - 1 - (R - 1 - r) % m

    if L >= R or x_min > x_max:
        return 0, x_min, x_max

    return (x_max - x_min) // m + 1, x_min, x_max

