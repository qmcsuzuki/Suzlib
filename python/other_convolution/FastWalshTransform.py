"""
in place な高速Walsh変換
xor畳み込みなどに用いる。
"""

def fwt_inplace(a):
    n = len(a)
    assert n&(n-1) == 0 # 長さは 2 ベキ
    i = 1
    while i < n:
        for j in range(n):
            if i&j==0:
                a[j], a[j|i] = a[j]+a[j|i], a[j]-a[j|i]
        i <<= 1
    for i in range(n):
        a[i] %= MOD

def ifwt_inplace(a):
    fwt_inplace(a)
    v = pow(len(a),MOD-2,MOD)
    for i in range(len(a)):
      a[i] = v*a[i]%MOD
