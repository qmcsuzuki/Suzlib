# competitive-verifier: TITLE Garner 法

from math import gcd

def Garner(a,m,already_coprime=True,permit0=True):
    """x == a[i] (mod m[i]) の最小非負解を大域変数 MOD で還元して返す。
    各 m[i] > 0、len(a) == len(m) を仮定する。
    already_coprime=True は法が互いに素のときだけ指定する。
    False では a,m を破壊的に同値な互いに素の法へ変換し、不整合なら -1。
    permit0=False では最小正解を返す（零解の場合は法の最小公倍数）。
    時間 O(len(a)^2 log max(m))。
    """
    assert len(a) == len(m)
    assert all(mi > 0 for mi in m)
    if not a:
        return (0 if permit0 else 1) % MOD

    def compute(i,M): # c[0] + c[1]m[0] + c[2]m[0]m[1] + ... c[i-1]m[0]...m[i-2] mod M を返す
        """確定した混合基数係数 c[0:i] の値を法 M で評価する。"""
        v = c[i-1]
        for j in range(i-2,-1,-1):
            v = (v*m[j] + c[j])%M
        return v
    # m を互いに素にする前計算。矛盾なら -1 を返す
    if already_coprime == 0 == Garner_coprimize(a,m):
        return -1
    # 以下、m は互いに素    
    # ans = c[0] + c[1]m[0] + c[2]m[0]m[1] + ... なる c を求める
    n = len(a)
    c = [0]*n
    c[0] = a[0] % m[0]
    for i in range(1,n):
        ms = 1
        for j in range(i): ms = ms*m[j]%m[i]
        c[i] = (a[i] - compute(i,m[i]))*pow(ms,-1,m[i])%m[i]
    if permit0 or any(ci for ci in c):
        v = c[n-1]
        for i in range(n-2,-1,-1):
            v = (v*m[i] + c[i])%MOD
        return v % MOD
    else:
        v = 1
        for mi in m: v = v*mi%MOD
        return v

def Garner_coprimize(a,m):
    """連立合同式を同値な互いに素の法へ破壊的に変換し、整合性を 0/1 で返す。"""
    n = len(a)
    for i in range(1,n):
        for j in range(i):
            g = gcd(m[j],m[i])
            if (a[i]-a[j])%g: return 0
            m[i] //= g
            m[j] //= g
            gi = gcd(g,m[i])
            gj = g//gi
            # 不変量 gi*gj のもとで、gj の素因数を gi にうつす
            g = gcd(gi,gj)
            while g > 1:
                gi *= g
                gj //= g
                g = gcd(gi,gj)
            m[i] *= gi
            m[j] *= gj
            a[i] %= m[i]
            a[j] %= m[j]
    return 1
