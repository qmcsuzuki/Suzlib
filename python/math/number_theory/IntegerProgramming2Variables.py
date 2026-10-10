# competitive-verifier: TITLE 2変数整数最適化

def integer_problem_2variables(a, b, s, t, u, L, R):
    """整数条件の下で ax+by の最大値を求める。

    制約は sx+ty <= u, L <= x <= R, y >= 0。
    s >= 0, t > 0, L <= R, s*L <= u を仮定する。
    a, b, L, u は負でもよい。最適解ではなく最適値を返す。
    ユークリッド互除法型の対数時間（整数演算を O(1) とする）。
    """
    assert s >= 0 and t > 0 and L <= R and s * L <= u
    if s:
        R = min(R, u // s)
    if b <= 0:
        return max(a * L, a * R)

    ans = a * L
    offset = 0
    while True:
        if L > R or s * L > u:
            return ans
        if L == R or a <= 0:
            return max(ans, offset + a * L + b * max(0, (u - s * L) // t))
        if s < t:
            # 長方形部分の最適値を保存し、残りの台形の座標を交換する。
            LL = (u - s * R) // t
            ans = max(ans, offset + a * R + b * LL)
            u -= s * L
            offset += a * L
            L, R = LL + 1, u // t
            a, b = b, a
            s, t = t, s
        else:
            # 区間右端を基準にした shear 変換（互除法）。
            c, s = divmod(s, t)
            a -= b * c
            offset += b * c * R
            u -= t * c * R


def knapsack_2variable(v1, v2, w1, w2, wmax):
    """非負整数 x,y に対する2品目ナップサックの最大価値を返す。

    w1*x+w2*y <= wmax の下で v1*x+v2*y を最大化する。
    v1,v2,wmax >= 0, w1,w2 > 0 を仮定する。対数時間。
    """
    assert v1 >= 0 and v2 >= 0 and w1 > 0 and w2 > 0 and wmax >= 0
    return integer_problem_2variables(
        v1, v2, w1, w2, wmax, 0, wmax // w1
    )


def knapsack_dual_2variable(v1, v2, w1, w2, wmin):
    """非負整数 x,y に対する2品目被覆問題の最小費用を返す。

    w1*x+w2*y >= wmin の下で v1*x+v2*y を最小化する。
    v1,v2,wmin >= 0, w1,w2 > 0 を仮定する。対数時間。
    dual は従来の関数名であり、線形計画の双対問題の意味ではない。
    """
    assert v1 >= 0 and v2 >= 0 and w1 > 0 and w2 > 0 and wmin >= 0
    if wmin == 0:
        return 0

    # x <= X の範囲を x'=X-x, y'=Y-y で最大化問題に帰着する。
    # x >= X+1 なら候補 (X+1,0) を調べれば十分。
    X = (wmin - 1) // w1
    Y = (wmin + w2 - 1) // w2
    U = w1 * X + w2 * Y - wmin
    saved = integer_problem_2variables(v1, v2, w1, w2, U, 0, X)
    return min(v1 * (X + 1), v1 * X + v2 * Y - saved)
