from math import gcd

def crt(RMlist):
    """
    x == r_i (mod m_i) (for all i) の解 x \eqiv r (mod m) を (r,m) の形で出力
    解がないときは (0,0)
    """
    r0, M0 = 0, 1

    for r1, M1 in RMlist:
        assert M1 > 0

        diff = (r1%M1) - r0
        g = gcd(M0, M1)
        if diff % g: return 0, 0

        u = M1 // g
        if u == 1: continue

        t = (diff // g) * pow(M0 // g, -1, u) % u
        r0 += t * M0
        M0 *= u
        r0 %= M0

    return r0, M0
