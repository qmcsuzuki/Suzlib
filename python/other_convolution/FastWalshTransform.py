"""
in place な高速Walsh変換
xor畳み込みなどに用いる。
配列 a の長さは2ベキ
M = max(a) のとき、max(fwt(a)) <= len(a)*M なので、
中でmodをとらなくても、オーバーフローはだいたいは大丈夫なはず

ifwt では、最後にまとめて len(a) で割り算していることに注意
H^2 = len(a)I なので。
"""

def fwt_inplace(a):
    n = len(a)
    i = 1
    while i < n:
        for j in range(n):
            if i&j==0:
                a[j], a[j|i] = a[j]+a[j|i], a[j]-a[j|i]
        i <<= 1
        
def ifwt_inplace(a):
    fwt(a)
    v = pow(len(a),MOD-2,MOD)
    for i in range(len(a)):
      a[i] = v*(a[i]%MOD)%MOD
