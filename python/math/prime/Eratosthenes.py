# competitive-verifier: TITLE エラトステネスの篩

"""
エラトステネスの篩: N以下の素数のリストを返す
#N=10**6で0.1secほど
"""
def Eratosthenes(N): #N以下の素数のリストを返す
    N+=1
    is_prime_list = [True]*N
    m = int(N**0.5)+1
    for i in range(3,m,2):
        if is_prime_list[i]:
            is_prime_list[i*i::2*i]=[False]*((N-i*i-1)//(2*i)+1)
    return [2] + [i for i in range(3,N,2) if is_prime_list[i]]

"""
is_prime_list を返すバージョン
"""
def Eratosthenes_is_prime_list(N): #N以下の素数のリストを返す
    #iが素数のときis_prime_list[i]=1，それ以外は0
    N+=1
    is_prime_list = [True]*N
    is_prime_list[0], is_prime_list[1] = False, False
    for j in range(4,N,2): is_prime_list[j] = False
    m = int(N**0.5)+1
    for i in range(3,m,2):
        if is_prime_list[i]:
            is_prime_list[i*i::2*i]=[False]*((N-i*i-1)//(2*i)+1)
    return is_prime_list
