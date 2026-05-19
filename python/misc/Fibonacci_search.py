# competitive-verifier: TITLE 黄金分割探索

"""
[l,r) で下に凸な関数 f の最小値を求める
"""
def Fibonacci_search(l,r,f):
    L = l-1
    a,b = 1,2
    while L+b <= r:
        a,b = b,a+b
    A,R = L+a, L+b
    fA = f(A)
    # 以下 (L,A,R) を管理
    while R-L > 2:
        B = L+R-A
        if B <= r:
            fB = f(B)
            if A > B:
                fA,fB,A,B = fB,fA,B,A
        if B <= r and fA > fB:
            L,A = A,B
            fA = fB
        else:
            R = B
    return A, fA
