# competitive-verifier: TITLE 行列演算ファクトリ（平坦化）
"""
1 次元化された有名な環上の行列について、（積演算 op, 単位行列）を返すファクトリ
行列は row-major の 1 次元 tuple/list で持つ。
"""

def make_minplus_matrix(K, INF):
    """
    min-plus 行列積
        C[i][j] = min_k (A[i][k] + B[k][j])
    単位行列は対角 0, 非対角 INF。
    """
    E = tuple(0 if i == j else INF for i in range(K) for j in range(K))

    def op(A, B):
        C = [INF] * (K * K)
        for i in range(K):
            iK = i * K
            for k in range(K):
                aik = A[iK + k]
                if aik == INF:
                    continue
                kK = k * K
                for j in range(K):
                    bkj = B[kK + j]
                    if bkj == INF:
                        continue
                    v = aik + bkj
                    if v < C[iK + j]:
                        C[iK + j] = v
        return tuple(C)

    return op, E


def make_maxplus_matrix(K, NEG_INF):
    """
    max-plus 行列積
        C[i][j] = max_k (A[i][k] + B[k][j])
    単位行列は対角 0, 非対角 NEG_INF。
    """
    E = tuple(0 if i == j else NEG_INF for i in range(K) for j in range(K))

    def op(A, B):
        C = [NEG_INF] * (K * K)
        for i in range(K):
            iK = i * K
            for k in range(K):
                aik = A[iK + k]
                if aik == NEG_INF:
                    continue
                kK = k * K
                for j in range(K):
                    bkj = B[kK + j]
                    if bkj == NEG_INF:
                        continue
                    v = aik + bkj
                    if v > C[iK + j]:
                        C[iK + j] = v
        return tuple(C)

    return op, E


def make_usual_matrix(K):
    """
    通常の行列積
        C[i][j] = sum_k A[i][k] * B[k][j]
    単位行列は通常の単位行列。
    """
    E = tuple(1 if i == j else 0 for i in range(K) for j in range(K))

    def op(A, B):
        C = [0] * (K * K)
        for i in range(K):
            iK = i * K
            for k in range(K):
                aik = A[iK + k]
                if aik == 0:
                    continue
                kK = k * K
                for j in range(K):
                    C[iK + j] += aik * B[kK + j]
        return tuple(C)

    return op, E


def make_MODint_matrix(K):
    """
    mod MOD 上の通常の行列積（MOD はグローバル変数前提）
        C[i][j] = sum_k A[i][k] * B[k][j] mod MOD
    単位行列は通常の単位行列。
    """
    E = tuple(1 if i == j else 0 for i in range(K) for j in range(K))

    def op(A, B):
        mod = MOD
        C = [0] * (K * K)
        for i in range(K):
            iK = i * K
            for k in range(K):
                aik = A[iK + k]
                if aik == 0:
                    continue
                kK = k * K
                for j in range(K):
                    C[iK + j] += aik * B[kK + j]
        for i in range(K * K):
            C[i] %= mod
        return tuple(C)

    return op, E


def make_bool_matrix(K):
    """
    boolean 行列積
        C[i][j] = OR_k (A[i][k] and B[k][j])
    単位行列は対角 True, 非対角 False。
    """
    E = tuple(i == j for i in range(K) for j in range(K))

    def op(A, B):
        C = [False] * (K * K)
        for i in range(K):
            iK = i * K
            for k in range(K):
                if not A[iK + k]:
                    continue
                kK = k * K
                for j in range(K):
                    if B[kK + j]:
                        C[iK + j] = True
        return tuple(C)

    return op, E


def make_maxmin_matrix(K, NEG_INF, INF):
    """
    max-min 行列積
        C[i][j] = max_k min(A[i][k], B[k][j])
    いわゆる bottleneck path 型。
    単位行列は対角 INF, 非対角 NEG_INF。
    """
    E = tuple(INF if i == j else NEG_INF for i in range(K) for j in range(K))

    def op(A, B):
        C = [NEG_INF] * (K * K)
        for i in range(K):
            iK = i * K
            for k in range(K):
                aik = A[iK + k]
                if aik == NEG_INF:
                    continue
                kK = k * K
                for j in range(K):
                    bkj = B[kK + j]
                    if bkj == NEG_INF:
                        continue
                    v = aik if aik < bkj else bkj
                    if v > C[iK + j]:
                        C[iK + j] = v
        return tuple(C)

    return op, E


def make_minmax_matrix(K, INF, NEG_INF):
    """
    min-max 行列積
        C[i][j] = min_k max(A[i][k], B[k][j])
    単位行列は対角 NEG_INF, 非対角 INF。
    """
    E = tuple(NEG_INF if i == j else INF for i in range(K) for j in range(K))

    def op(A, B):
        C = [INF] * (K * K)
        for i in range(K):
            iK = i * K
            for k in range(K):
                aik = A[iK + k]
                if aik == INF:
                    continue
                kK = k * K
                for j in range(K):
                    bkj = B[kK + j]
                    if bkj == INF:
                        continue
                    v = aik if aik > bkj else bkj
                    if v < C[iK + j]:
                        C[iK + j] = v
        return tuple(C)

    return op, E
