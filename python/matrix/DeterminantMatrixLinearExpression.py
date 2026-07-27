# competitive-verifier: TITLE 特性多項式と一次式行列の行列式

"""
素数 MOD 上で det(M0 + x M1) を求める。

係数は定数項から昇順に並べる。
入力行列は変更しない。
"""


def _characteristic_polynomial_hessenberg(H):
    """上 Hessenberg 行列 H の特性多項式を La Budde 型漸化式で求める。"""
    n = len(H)
    P = [[1]]

    for i in range(n):
        f = [0] * (i + 2)
        g = P[i]
        diag = H[i][i]

        # (x - H[i][i]) P[i]
        for k in range(i + 1):
            v = g[k]
            f[k + 1] = (f[k + 1] + v) % MOD
            f[k] = (f[k] - diag * v) % MOD

        # -H[j][i] H[j+1][j] ... H[i][i-1] P[j]
        prod = 1
        for j in range(i - 1, -1, -1):
            prod = prod * H[j + 1][j] % MOD
            coef = -H[j][i] * prod % MOD
            g = P[j]
            for k in range(j + 1):
                f[k] = (f[k] + coef * g[k]) % MOD
        P.append(f)

    return P[-1]


def characteristic_polynomial(A):
    """
    正方行列 A の特性多項式 det(xI-A) を返す。

    返り値 f は f[i] が x^i の係数。計算量 O(N^3)、メモリ O(N^2)。
    MOD は素数とする。
    """
    n = len(A)
    assert all(len(row) == n for row in A)
    H = [[v % MOD for v in row] for row in A]

    # 相似変換で上 Hessenberg 化する。
    for k in range(n - 2):
        pivot = k + 1
        while pivot < n and H[pivot][k] == 0:
            pivot += 1
        if pivot == n:
            continue

        if pivot != k + 1:
            H[k + 1], H[pivot] = H[pivot], H[k + 1]
            for row in H:
                row[k + 1], row[pivot] = row[pivot], row[k + 1]

        inv = pow(H[k + 1][k], MOD - 2, MOD)
        base = H[k + 1]
        for i in range(k + 2, n):
            if H[i][k] == 0:
                continue
            q = H[i][k] * inv % MOD
            row = H[i]
            row[k] = 0
            for j in range(k + 1, n):
                row[j] = (row[j] - q * base[j]) % MOD
            for j in range(n):
                H[j][k + 1] = (H[j][k + 1] + q * H[j][i]) % MOD

    return _characteristic_polynomial_hessenberg(H)


def determinant_matrix_linear_expression(M0, M1):
    """
    det(M0 + x M1) を返す。

    返り値 f は長さ N+1 で、f[i] が x^i の係数。
    M1 が特異でもよい。計算量 O(N^3)、メモリ O(N^2)。
    MOD は素数とする。

    M1 を上三角化する。pivot が存在しない列では、その列の M1 成分を
    列基本変形で 0 にしてから M0 と M1 の列を交換する。この交換は
    行列束の対応する列を x 倍することに相当する。
    """
    n = len(M0)
    assert len(M1) == n
    assert all(len(row) == n for row in M0)
    assert all(len(row) == n for row in M1)
    if n == 0:
        return [1]

    B = [[v % MOD for v in row] for row in M0]
    U = [[v % MOD for v in row] for row in M1]
    inv_diag = [0] * n
    shift = 0
    sign = 1

    p = 0
    while p < n:
        pivot = p
        while pivot < n and U[pivot][p] == 0:
            pivot += 1

        if pivot == n:
            # U[:p][:p] c = U[:p][p] を解き、
            # column(p) -= sum(c[j] column(j)) とする。
            c = [0] * p
            for i in range(p - 1, -1, -1):
                v = U[i][p]
                row = U[i]
                for j in range(i + 1, p):
                    v = (v - row[j] * c[j]) % MOD
                c[i] = v * inv_diag[i] % MOD

            for i in range(n):
                row = B[i]
                v = row[p]
                for j in range(p):
                    v = (v - row[j] * c[j]) % MOD
                row[p] = v

            # U の第 p 列は上の列変形で 0。係数を交換すると x 倍になる。
            for i in range(n):
                U[i][p] = B[i][p]
                B[i][p] = 0

            shift += 1
            if shift > n:
                return [0] * (n + 1)
            continue

        if pivot != p:
            U[p], U[pivot] = U[pivot], U[p]
            B[p], B[pivot] = B[pivot], B[p]
            sign = -sign

        pivot_value = U[p][p]
        inv = pow(pivot_value, MOD - 2, MOD)
        inv_diag[p] = inv
        base_u = U[p]
        base_b = B[p]

        for i in range(p + 1, n):
            if U[i][p] == 0:
                continue
            q = U[i][p] * inv % MOD
            row_u = U[i]
            row_b = B[i]
            row_u[p] = 0
            for j in range(p + 1, n):
                row_u[j] = (row_u[j] - q * base_u[j]) % MOD
            for j in range(n):
                row_b[j] = (row_b[j] - q * base_b[j]) % MOD
        p += 1

    # C = U^{-1} B。U 自体を I にする Gauss-Jordan は行わない。
    C = [row[:] for row in B]
    for i in range(n - 1, -1, -1):
        row = C[i]
        for k in range(i + 1, n):
            q = U[i][k]
            if q == 0:
                continue
            src = C[k]
            for j in range(n):
                row[j] = (row[j] - q * src[j]) % MOD
        inv = inv_diag[i]
        for j in range(n):
            row[j] = row[j] * inv % MOD

    # det(B+xU) = det(U) det(xI+C)。
    # characteristic_polynomial(-C) = det(xI+C)。
    for i in range(n):
        row = C[i]
        for j in range(n):
            row[j] = -row[j] % MOD
    f = characteristic_polynomial(C)

    scale = sign % MOD
    for i in range(n):
        scale = scale * U[i][i] % MOD

    # 現在の行列式 = sign * x^shift * 元の行列式。
    res = [0] * (n + 1)
    for i in range(shift, n + 1):
        res[i - shift] = f[i] * scale % MOD
    return res
