# competitive-verifier: TITLE 原始根

"""
奇素数 p の原始根 g を求める
i.e., g^n = 1 (mod p) となる n の最小値は p-1
"""
@lru_cache(maxsize=None)
def primitive_root(p):
    assert p%2
    lst = prime_factorize(p-1)
    for g in range(2,p):
        for q,_ in lst:
            if pow(g,(p-1)//q,p) == 1:
                break
        else:
            return g

"""
奇素数 p に対して
p^e の原始根 g を求める
i.e., g^n = 1 (mod p^e) となる n の最小値は (p-1)p^{e-1}
"""
def primitive_power_root(p,e):
    assert e >= 1
    g = primitive_root(p)
    if e == 1:
        return g
    if pow(g,p-1,p**2)==1: # g or g+p で OK
        g += p
    return g
