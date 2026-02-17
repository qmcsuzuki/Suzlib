# competitive-verifier: TITLE 最小素因数による素因数分解

"""
最小素因数の配列を返す
"""
def Eratosthenes_spf_list(N):
    # i>=2 のとき spf_list[i] は i の最小素因数
    # 0,1 については便宜上 0 を入れる
    N += 1
    if N <= 0:
        return []
    spf_list = list(range(N))
    if N >= 1:
        spf_list[0] = 0
    if N >= 2:
        spf_list[1] = 0
    for i in range(4,N,2):
        spf_list[i] = 2
    m = int(N**0.5)+1
    for i in range(3,m,2):
        if spf_list[i] == i:
            for j in range(i*i,N,2*i):
                if spf_list[j] == j:
                    spf_list[j] = i
    return spf_list

"""
素因数を（重複ありの）リストで返す
"""
def factorize(n):
    if n <= 1:
        return []
    spf_list = Eratosthenes_spf_list(n)
    res = []
    while n > 1:
        p = spf_list[n]
        res.append(p)
        n //= p
    return res


