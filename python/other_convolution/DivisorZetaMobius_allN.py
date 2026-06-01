# competitive-verifier: TITLE 約数包除（N 以下の整数全て）

#aを破壊的にgcd-zetaする(０方向に)
def zeta_gcd(a,primes):
    n = len(a)-1
    for p in primes:
        for i in range(n//p,0,-1):
            a[i] += a[p*i]
            a[i] %= MOD
#    return a

#aを破壊的にgcd-mobiusする(０方向に)
def mobius_gcd(a,primes):
    n = len(a)
    for p in primes:
        for i in range(1,n):
            if i*p >= n: break
            a[i] -= a[p*i] 
            a[i] %= MOD
#    return a

#aを破壊的にgcd-zetaする(n方向に)
def zeta_gcd_to_n(a,primes):
    n = len(a)-1
    for p in primes:
        for i in range(1,1+n//p):
            a[p*i] += a[i]
            a[p*i] %= MOD

#aを破壊的にgcd-mobiusする(n 方向に)
def zeta_mobius_to_n(a,primes):
    n = len(a)-1
    for p in primes:
        for i in range(n//p,0,-1):
            a[p*i] -= a[i]
            a[p*i] %= MOD
#    return a
