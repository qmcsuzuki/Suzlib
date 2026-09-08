# competitive-verifier: TITLE 最小素因数列挙と O(log N) 素因数分解

"""
最小素因数の配列 spf_list を返す。時間 O(N log log N)、空間 O(N)。
"""
def Eratosthenes_spf_list(N):
    """N 以下の各整数の最小素因数を配列で返し、0 と 1 には 0 を格納する。"""
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
素因数を（重複ありの）リスト [p1,p2,p3,...] で返す。
spf_list=Eratosthenes_spf_list(N) を渡せば、1 <= n <= N の各呼び出しは O(log n)。
省略時は従来どおり篩も作るため、時間 O(n log log n)、空間 O(n)。
n <= 1 は従来どおり [] を返す。
"""
def factorize(n, spf_list=None):
    """最小素因数表を利用して素因数を重複付きリストで返し、表の省略時は前計算も行う。"""
    if n <= 1:
        return []
    if spf_list is None:
        spf_list = Eratosthenes_spf_list(n)
    assert n < len(spf_list)
    res = []
    while n > 1:
        p = spf_list[n]
        res.append(p)
        n //= p
    return res


