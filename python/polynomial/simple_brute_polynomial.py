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
        for j in range(L-i):
            res[i+j] = (res[i+j] + v*g[j])%MOD
    return res
  
# https://atcoder.jp/contests/abc399/submissions/64365608
