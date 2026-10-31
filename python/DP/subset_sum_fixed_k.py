# competitive-verifier: TITLE 要素数 3・4 の部分和（整数での数え上げ・復元）
"""
正整数の多重集合 A から K=3,4 個を選び、和を M にできるか判定・構築する
L=len(A), N=max(A) として時間 O(L+N log(N+1))。数え上げは集合専用。
引数 convolution(a, b) は mod 998244353 の畳み込みを返す関数を渡す
"""


def _prepare(A, K, M, convolution, multiset=False):
    assert K in (3, 4)
    A = list(A)
    assert all(a > 0 for a in A)
    if multiset:
        counts = {}
        for a in A:
            counts[a] = min(counts.get(a, 0) + 1, K)
        A = [a for a, count in counts.items() for _ in range(count)]
    else:
        assert len(set(A)) == len(A)
    assert len(A) < 998244353
    if len(A) < K or M < K or M > K * max(A, default=0):
        return None
    f = [0] * (max(A) + 1)
    for a in A:
        f[a] += 1
    q = _convolve_frequency(f, f, len(A), convolution)
    return A, f, q


def _get(f, i):
    return f[i] if 0 <= i < len(f) else 0


def count_subset_sum(A, K, M, convolution):
    """相異なる正整数の集合から和 M の K 要素部分集合の真の個数を返す。畳み込み1回、O(N log(N+1))。"""
    data = _prepare(A, K, M, convolution)
    if data is None:
        return 0
    return _count(*data, K, M)


def exists_subset_sum(A, K, M, convolution):
    """正整数の多重集合から K=3,4 個選んで和 M にできるか返す。

    同値の要素は高々 K 個に制限する。入力は変更しない。
    L=len(A), N=max(A) として時間 O(L+N log(N+1))、空間 O(L+N)。
    """
    data = _prepare(A, K, M, convolution, multiset=True)
    return data is not None and _count(*data, K, M) > 0


def _count(A, f, q, K, M):
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
        # 特定の1要素 a を含むペアの数を除く（同値の別要素は使用可）。
        b = M - 2*a
        if _get(pairs, M-a) > _get(f, b) - (b == a):
            for b in A:
                c = M - a - b
                if f[b] > (b == a) and _get(f, c) > (c == a) + (c == b):
                    return [a, b, c]
    return None


def _convolve_frequency(p, f, n, convolution):
    # f は非負の頻度列。係数上界 n*max(p) が法未満なら分割不要。
    if max(p, default=0) * n < 998244353:
        return convolution(p, f)
    return _convolve_integer_binary(p, f, n, convolution)


def _convolve_integer_binary(p, f, n, convolution):
    """非負整数列 p と 係数和 n < mod の非負整数列 f の整数畳み込み。"""
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
    """正整数の多重集合から和 M の K=3,4 個の値を返す。解なしは None。

    同じ値も入力の個数まで使用できる。返り値は添字ではなく値のリスト。
    同値の要素は高々 K 個に制限し、入力は変更しない。順序の保証はない。
    L=len(A), N=max(A) として時間 O(L+N log(N+1))、空間 O(L+N)。
    """
    data = _prepare(A, K, M, convolution, multiset=True)
    if data is None:
        return None
    A, f, q = data
    pairs = q[:]
    for a in A:
        pairs[2*a] -= 1
    pairs = [v // 2 for v in pairs]
    if K == 3:
        return _find_three(A, f, pairs, M)

    pf = _convolve_integer_binary(pairs, f, len(A), convolution)
    f2 = [0] * (2*len(f) - 1)
    f2[::2] = f
    f2f = _convolve_frequency(f2, f, len(A), convolution)
    # E3 = (E2*f - f(x^2)*f + f(x^3))/3。
    for a in A:
        t = M - a
        triples = (_get(pf, t) - _get(f2f, t)
                   + (t % 3 == 0)*_get(f, t//3)) // 3
        # a を含む三つ組の数は E2[M-2a]-f[M-3a]+[M=4a]。
        if triples - _get(pairs, M-2*a) + _get(f, M-3*a) - (M == 4*a) > 0:
            # 特定の1要素 a だけを除いた多重集合へ更新。
            A.remove(a)
            for b in A:
                pairs[a+b] -= 1
            f[a] -= 1
            rest = _find_three(A, f, pairs, t)
            assert rest is not None
            return [a] + rest
    return None

