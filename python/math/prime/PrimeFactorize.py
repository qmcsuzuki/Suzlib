"""
O(\sqrt N) 素因数分解
input: N
output: [[p1,e1],[p2,e2],...] の形で素因数分解する。
        N=1なら空のリストを返す
"""
def prime_factorize(N):
    exponent = 0
    while N%2 == 0:
        exponent += 1
        N //= 2
    if exponent: factorization = [[2,exponent]]
    else: factorization = []
    i=1
    while i*i <=N:
        i += 2
        if N%i: continue
        exponent = 0
        while N%i == 0:
            exponent += 1
            N //= i
        factorization.append([i,exponent])
    if N!= 1: factorization.append([N,1])
    assert N != 0, "zero"
    return factorization
