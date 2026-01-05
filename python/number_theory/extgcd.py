# verification-helper: TITLE 拡張ユークリッドの互除法

def extgcd(a,b):
    x1 = y0 = 0
    x0 = y1 = 1
    while b:
        q = a//b
        x0,x1 = x1, x0 - q*x1
        y0,y1 = y1, y0 - q*y1
        a,b = b, a - q*b
    return x0, y0, a

