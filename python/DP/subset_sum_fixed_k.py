# competitive-verifier: TITLE 要素数 3・4 の部分和（整数での数え上げ・復元）
"""相異なる正整数 A から K=3,4 個を選び、和を M にする。

convolution(a, b) は mod 998244353 の畳み込みを返す関数を渡す。
入力を変更せず、長さ len(a)+len(b)-1 の標準剰余のリストを返すこと。
N=max(A), n=len(A)。n < 998244353 を仮定する。
通常の NTT では、復元なし/K=3 は 2N+1 <= 2^23、K=4 の復元は
3N+1 <= 2^23 が必要。利用する convolution の長さ制限にも従う。

count_subset_sum: 真の個数（剰余ではない）。存在判定は返り値 > 0。
find_subset_sum: 選んだ値 K 個のリスト。解なしは None。添字ではない。
数え上げ/K=3 復元は畳み込み1回。K=4 復元は係数分割を用いる。
時間 O(N log(N+1))、空間 O(N)（上記の NTT 長さ制限下、整数演算単位）。
"""


def _prepare(A, K, M, convolution):
    assert K in (3, 4)
    A = list(A)
    assert all(a > 0 for a in A) and len(set(A)) == len(A)
    assert len(A) < 998244353
    if len(A) < K or M < K or M > K * max(A, default=0):
        return None
    f = [0] * (max(A) + 1)
    for a in A:
        f[a] = 1
    q = convolution(f, f)
    # q[s] <= n < mod なので、q は整数として正確。
    return A, f, q


def _get(f, i):
    return f[i] if 0 <= i < len(f) else 0


def count_subset_sum(A, K, M, convolution):
    """和 M の K 要素部分集合の真の個数。畳み込み1回、O(N log(N+1))。"""
    data = _prepare(A, K, M, convolution)
    if data is None:
        return 0
    A, f, q = data
    get = _get
    # Newton の恒等式。以下はすべて Python の整数演算。
    if K == 3:
        return (sum(get(q, M-a) - 3*get(f, M-2*a) for a in A)
                + 2*(M % 3 == 0)*get(f, M//3)) // 6
    return (sum(v * get(q, M-s) for s, v in enumerate(q))
            - 6*sum(get(q, M-2*a) for a in A)
            + 3*(M % 2 == 0)*get(q, M//2)
            + 8*sum(get(f, M-3*a) for a in A)
            - 6*(M % 4 == 0)*get(f, M//4)) // 24


def _find_three(A, f, pairs, M):
    for a in A:
        # a を含むペア {a, M-2a} を除く。
        b = M - 2*a
        if _get(pairs, M-a) > (b != a and _get(f, b)):
            for b in A:
                c = M - a - b
                if b != a and c != a and c != b and _get(f, c):
                    return [a, b, c]
    return None


def _convolve_integer_binary(p, f, n, convolution):
    """非負整数列 p と n 個の 1 を持つ 0/1 列 f の整数畳み込み。"""
    # 各桁の畳み込み係数 <= n*(base-1) < mod。
    base = (998244353 - 1) // n + 1
    result = [0] * (len(p) + len(f) - 1)
    rest = p[:]
    weight = 1
    while any(rest):
        digit = [v % base for v in rest]
        product = convolution(digit, f)
        for i, v in enumerate(product):
            result[i] += weight * v
        rest = [v // base for v in rest]
        weight *= base
    return result


def find_subset_sum(A, K, M, convolution):
    """和 M の相異なる K 個の値を返す。解なしは None。O(N log(N+1))。"""
    data = _prepare(A, K, M, convolution)
    if data is None:
        return None
    A, f, q = data
    pairs = [v // 2 for v in q]  # 対角項は 0/1 なので切り捨てで除ける。
    if K == 3:
        return _find_three(A, f, pairs, M)

    pf = _convolve_integer_binary(pairs, f, len(A), convolution)
    f2 = [0] * (2*len(f) - 1)
    f2[::2] = f
    f2f = convolution(f2, f)  # 係数 <= n、したがって整数として正確。
    # E3 = (E2*f - f(x^2)*f + f(x^3))/3。
    for a in A:
        t = M - a
        triples = (_get(pf, t) - _get(f2f, t)
                   + (t % 3 == 0)*_get(f, t//3)) // 3
        # a を含む三つ組の数は E2[M-2a]-f[M-3a]+[M=4a]。
        if triples - _get(pairs, M-2*a) + _get(f, M-3*a) - (M == 4*a) > 0:
            # a を除いた集合のペア数へ更新し、3要素復元に帰着。
            for b in A:
                if b != a:
                    pairs[a+b] -= 1
            f[a] = 0
            rest = _find_three([b for b in A if b != a], f, pairs, t)
            assert rest is not None
            return [a] + rest
    return None
