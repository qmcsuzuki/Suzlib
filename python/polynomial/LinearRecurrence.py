# competitive-verifier: TITLE Linear Recurrence

def Berlecamp_Massay(A):
    n = len(A)
    C = [1]
    B = [1]
    L = 0
    m = 1
    b = 1
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
    Q = C
    P = polymul(A, Q)[:n]
    return P, Q


def nth_term(p, q, n=None):
    if n is None:
        try:
            n = N
        except NameError as exc:
            raise ValueError("n is required") from exc
    p = p[:]
    q = q[:]
    while n > 0:
        q_neg = [coef if i % 2 == 0 else (-coef) % MOD for i, coef in enumerate(q)]
        pq = polymul(p, q_neg)
        qq = polymul(q, q_neg)
        p = pq[::2] if n % 2 == 0 else pq[1::2]
        q = qq[::2]
        n //= 2
    return p[0] * pow(q[0], MOD - 2, MOD) % MOD
