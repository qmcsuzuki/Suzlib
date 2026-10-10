# competitive-verifier: TITLE 剰余列の格子点凸包

def lattice_prefix_min(M, A, B, R):
    """(Ax+B)%M (0 <= x <= R) の累積最小値の下側凸包を圧縮して返す。

    返り値 (xs, steps) は頂点の x 座標と各辺の公差ベクトル。
    steps[i]=(dx,dy) は xs[i] から xs[i+1] までの辺に沿った
    1 ステップを表す（端点間の差とは限らない）。
    len(steps)==len(xs)-1。同一直線上の記録点は圧縮される。
    M>0, R>=0 を仮定し、O(log M) 時間（整数演算を O(1) とする）。
    """
    assert M > 0 and R >= 0
    A %= M
    a, b, c, d = 0, 1, 1, 0
    x0, y0 = 0, B % M
    xs, steps = [0], []
    dhigh, dlow = M, A
    while y0 > 0 and dhigh and dlow:
        if y0 >= dhigh:
            n = min(y0 // dhigh, (R - x0) // d)
            if n <= 0:
                break
            y0 -= n * dhigh
            x0 += n * d
            xs.append(x0)
            steps.append((d, -dhigh))
        elif dhigh < dlow:
            n = dlow // dhigh
            a += c * n
            b += d * n
            dlow = b * A - a * M
        else:
            n = min(dhigh // dlow, (dhigh - y0 + dlow - 1) // dlow)
            if n <= 0:
                break
            c += a * n
            d += b * n
            dhigh = c * M - d * A
    return xs, steps


def lattice_lower_convex_hull(M, A, B, L, R):
    """点 (x,(Ax+B)%M), L <= x <= R の下側凸包を圧縮して返す。

    返り値は (xs, steps)。steps は各辺の公差ベクトルであり、
    len(steps)==len(xs)-1。同一直線上の点は圧縮される。
    M>0, L<=R を仮定する。O(log M) 時間。
    """
    assert M > 0 and L <= R
    left, dl = lattice_prefix_min(M, A, B + A * L, R - L)
    right, dr = lattice_prefix_min(M, -A, B + A * R, R - L)
    left = [L + x for x in left]
    right = [R - x for x in right]
    dr = [(dx, -dy) for dx, dy in dr]

    if left[-1] == right[-1]:
        left.pop()  # 左右で共通する最小点は1度だけ残す。
    else:
        dl.append((right[-1] - left[-1], 0))
    return left + right[::-1], dl + dr[::-1]


def lattice_prefix_min_hull(M, A, B, R):
    """lattice_prefix_min の x 座標だけを返す。O(log M) 時間。"""
    return lattice_prefix_min(M, A, B, R)[0]


def under_line_upper_hull(a, b, N, L, R):
    """y=floor((N-a*x)/b), L<=x<=R の上側凸包を返す。

    返り値は (xs,ys,dxs)。dxs は各辺に沿った x の公差で、
    len(dxs)==len(xs)-1。b>0, L<=R を仮定する。
    y>=0 の制約は課さない。O(log b) 時間。
    """
    assert b > 0 and L <= R
    xs, steps = lattice_lower_convex_hull(b, -a, N, L, R)
    ys = [(N - a * x) // b for x in xs]
    return xs, ys, [dx for dx, _ in steps]


def in_triangle(a, b, N):
    """ax+by<=N の非負整数点の線形最大化候補 (xs,ys) を返す。

    a,b>0, N>=0。目的関数 p*x+q*y は p,q>=0 を想定する。
    最適値を返す関数ではない。O(log b) 時間。
    """
    assert a > 0 and b > 0 and N >= 0
    xs, ys, _ = under_line_upper_hull(a, b, N, 0, N // a)
    return xs, ys


def out_of_triangle(a, b, N):
    """ax+by>=N の非負整数点の線形最小化候補 (xs,ys) を返す。

    a,b>0, N>=0。目的関数 p*x+q*y は p,q>=0 を想定する。
    y=0 の右端候補も含む。最適値ではなく候補点を返す。
    O(log b) 時間。
    """
    assert a > 0 and b > 0 and N >= 0
    if N == 0:
        return [0], [0]
    X = (N - 1) // a
    xs, _ = lattice_lower_convex_hull(b, a, -N, 0, X)
    xs.append(X + 1)
    ys = [max(0, (N - a * x + b - 1) // b) for x in xs]
    return xs, ys
