# competitive-verifier: TITLE 自分より小さい値で一番近いものの位置（all nearest smaller values）

"""
L[i]: A[l] < A[i] かつ l < i なる最大の l（存在しないなら -1）
R[i]: A[r] >= A[i] かつ r > i なる最小の r （存在しないなら len(A)）
左、右で不等号にイコールが入るかどうかが異なることに注意
# 不変条件: ループ終了時、\cdots A[L[L[r]]] < A[L[r]]  < A[r] で、右側の nearest smaller が未決定はこれらだけ
"""
def nearest_smaller(A):
    n = len(A)
    L = [-1]*n # nearest (strictly) smaller (left)
    R = [n]*n # nearest (non-strictly) smaller (right)
    for r in range(n):
        i = r-1
        while i != -1 and A[i] >= A[r]:
            R[i] = r
            i = L[i]
        L[r] = i
    return L,R


def nearest_larger(A):
    """
    L[i]: A[l] > A[i] かつ l < i なる最大の l（存在しないなら -1）
    R[i]: A[r] <= A[i] かつ r > i なる最小の r （存在しないなら len(A)）
    左、右で不等号にイコールが入るかどうかが異なることに注意
    nearest_smaller を利用して実装する
    """
    inverted = [-a for a in A]
    return nearest_smaller(inverted)
