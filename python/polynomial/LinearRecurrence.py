# competitive-verifier: TITLE Linear Recurrence

from python.polynomial.simple_brute_polynomial import polymul

# A = P(x)/Q(x)
def Berlecamp_Massey_with_generating_function(A):
    Q = Berlecamp_Massey(A)
    P = polymul(A, Q)[:len(Q)-1]
    return P, Q

# find minimal recurrence C:
# A[i] + C[0]A[i-1] + C[1]A[i-2] + ... + C[L-1]A[i-L] = 0
def Berlecamp_Massey(A):
    n = len(A)
    C = [1]
    B = [1]
    L = 0
    m = b = 1
    for i in range(n):
        d = A[i]
        for j in range(1, L + 1):
            d = (d + C[j] * A[i - j]) % MOD
        if d == 0:
            m += 1
            continue
        coef = d * pow(b, MOD - 2, MOD) % MOD
        T = C[:]
        if len(C) < len(B) + m:
            C += [0] * (len(B) + m - len(C))
        for j in range(len(B)):
            C[j + m] = (C[j + m] - coef * B[j]) % MOD
        if 2 * L <= i:
            L = i + 1 - L
            B = T
            b = d
            m = 1
        else:
            m += 1
    return C
# 母関数が f(x)/g(x) で与えられる線形漸化式の第 n 項
def fps_nth_term(f,g,N):
    assert g[0] != 0
    while N:
        h = g[:]
        for i in range(1,len(g),2):
            h[i] = -h[i]
        f = polymul(f,h)[N%2:N+1:2]
        g = polymul(g,h)[:N+1:2]
        N //= 2
    return f[0]*pow(g[0],MOD-2,MOD)%MOD

# a[0],...,a[L-1] とL次特性多項式 g が与えられているL項間漸化式の第N項
def rec_nth_term(a,g,N):
    L = len(g) - 1
    assert len(a) == L
    f = polymul(a,g)[:L-1]
    return fps_nth_term(f,g,N)
