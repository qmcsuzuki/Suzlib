# competitive-verifier: TITLE 素朴多項式演算

def polyadd(f,g):
    L = max(len(f),len(g))
    res = f[::] + [0]*(L-len(f))
    for i,v in enumerate(g):
        res[i] = (res[i]+v)%MOD
    return res

def polysub(f,g):
    L = max(len(f),len(g))
    res = f[::] + [0]*(L-len(f))
    for i,v in enumerate(g):
        res[i] = (res[i]-v)%MOD
    return res

def polymul(f,g,maxdegree=None):
    L = len(f)+len(g)-1
    if maxdegree is not None:
        L = min(L, maxdegree+1)
    res = [0]*L
    for i,v in enumerate(f):
        for j in range(min(len(g), L-i)):
            res[i+j] = (res[i+j] + v*g[j])%MOD
    return res

def polydivmod(f,g):
    """Naive long division; g[-1]!=0. Returns (quotient, remainder). O(N^2)."""
    assert g[-1] != 0
    if len(f) < len(g):
        return [0], polytrim(f[::])
    m = len(g)-1
    qdeg = (len(f)-1)-m
    q = [0]*(qdeg+1)
    r = f[::]
    invgl = pow(g[-1], MOD-2, MOD)
    for k in range(qdeg, -1, -1):
        coeff = r[m+k]*invgl%MOD
        q[k] = coeff
        for j in range(m+1):
            r[j+k] = (r[j+k] - coeff*g[j])%MOD
    return polytrim(q), polytrim(r)

def polytrim(f):
    """Remove trailing zeros; returns [0] for zero polynomial. O(N)."""
    i = len(f)-1
    while i > 0 and f[i] == 0:
        i -= 1
    return f[:i+1]

def FPSinv(f,n):
    """Series inverse up to n terms; f[0]!=0. Returns length n. O(N^2)."""
    assert f[0] != 0, "constant term is 0"
    if n <= 0:
        return []
    invf0 = pow(f[0], MOD-2, MOD)
    res = [0]*n
    res[0] = invf0
    for i in range(1,n):
        s = 0
        for j in range(1,i+1):
            if j < len(f):
                s = (s + f[j]*res[i-j])%MOD
        res[i] = (-s*invf0)%MOD
    return res

def polyderiv(f):
    """Derivative: f[i]*i. Returns degree-1 list or [0]. O(N)."""
    if len(f) <= 1:
        return [0]
    res = [0]*(len(f)-1)
    for i in range(1,len(f)):
        res[i-1] = f[i]*i%MOD
    return res

def polyinteg(f):
    """Integral with constant 0 using modular inverse. Returns length+1. O(N)."""
    res = [0]*(len(f)+1)
    for i,v in enumerate(f):
        res[i+1] = v*pow(i+1, MOD-2, MOD)%MOD
    return res


def FPSlog(f,n):
    """Log series up to n terms; requires f[0]==1. Returns length n. O(N^2)."""
    if n <= 0:
        return []
    if n == 1:
        return [0]
    der = polyderiv(f)
    inv = FPSinv(f, n-1)
    prod = polymul(der, inv, maxdegree=n-2)
    return polyinteg(prod)[:n]

def FPSexp(f,n):
    """Exp series up to n terms; requires f[0]==0. Returns length n. O(N^2)."""
    if n <= 0:
        return []
    res = [0]*n
    res[0] = 1
    der = polyderiv(f)
    for k in range(1,n):
        s = 0
        for i in range(k):
            j = k-1-i
            if j < len(der):
                s = (s + res[i]*der[j])%MOD
        res[k] = s*pow(k, MOD-2, MOD)%MOD
    return res

def polypow(f,k,n):
    """Power series up to n terms. Handles leading zero shift. Returns length n. O(N^2)."""
    if n <= 0:
        return []
    if k == 0:
        return [1] + [0]*(n-1)
    if f[0] != 0:
        invf0 = pow(f[0], MOD-2, MOD)
        g = [v*invf0%MOD for v in f]
        logf = FPSlog(g, n)
        for i in range(len(logf)):
            logf[i] = logf[i]*k%MOD
        res = FPSexp(logf, n)
        scale = pow(f[0], k, MOD)
        for i in range(len(res)):
            res[i] = res[i]*scale%MOD
        return res
    shift = 0
    while shift < len(f) and f[shift] == 0:
        shift += 1
    if shift == len(f):
        return [0]*n
    if shift*k >= n:
        return [0]*n
    g = f[shift:]
    invg0 = pow(g[0], MOD-2, MOD)
    h = [v*invg0%MOD for v in g]
    logg = FPSlog(h, n-shift*k)
    for i in range(len(logg)):
        logg[i] = logg[i]*k%MOD
    powg = FPSexp(logg, n-shift*k)
    scale = pow(g[0], k, MOD)
    for i in range(len(powg)):
        powg[i] = powg[i]*scale%MOD
    return [0]*(shift*k) + powg
  
# https://atcoder.jp/contests/abc399/submissions/64365608
