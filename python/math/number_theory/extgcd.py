# competitive-verifier: TITLE 拡張ユークリッドの互除法/1 変数 1 次方程式の解

def extgcd(a,b):
    x1 = y0 = 0
    x0 = y1 = 1
    while b:
        q = a//b
        x0,x1 = x1, x0 - q*x1
        y0,y1 = y1, y0 - q*y1
        a,b = b, a - q*b
    return a, x0, y0

def solve_linear_congruence(a: int, b: int, MOD: int) -> tuple[int, int]
    """
    ax = b (mod MOD) の解 x = r (mod m) を (r,m) で返す。解なしなら (0,0)
    """
    g, x, _ = extgcd(a, mod)
    if b % g: return (0,0)
    m0 = MOD // g
    return (x * (b // g)) % m0, m0
