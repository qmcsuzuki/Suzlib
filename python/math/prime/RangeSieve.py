# competitive-verifier: TITLE 区間エラトステネスの篩

"""
区間篩: R-L および \sqrt(R) が十分小さいとき、
L 以上 R 以下の数が素数かどうかを offset 付きの配列で返す
"""
def RangeSieve(L,R):
    assert 0 <= L <= R
    Eratosthenes_prime_lst = Eratosthenes(int(R**0.5)+1)
    is_prime = [1]*(R-L+1)
    for v in range(2): # 0,1 は素数でない
        if L <= v <= R:
            is_prime[L-v] = 0
    for p in Eratosthenes_prime_lst:
        for i in range((L+p-1)//p*p,R+1,p):
            if i != p: is_prime[i-L] = 0
    return Eratosthenes_prime_lst, is_prime
