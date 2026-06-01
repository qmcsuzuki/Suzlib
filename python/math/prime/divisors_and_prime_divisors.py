# competitive-verifier: TITLE 約数列挙・素因数列挙

def divisors_and_prime_divisors(n):
    """
    n の約数のリスト divs と素因数のリスト（重複なし） primes を返す
    """
    nn = n
    divs = []
    primes = []

    i = 1
    while i*i <= n:
        if n%i == 0:
            divs.append(i)
            if i*i != n:
                divs.append(n//i)

        if i >= 2 and nn%i == 0:
            primes.append(i)
            while nn%i == 0:
                nn //= i
        i += 1

    if nn > 1:
        primes.append(nn)

    divs.sort()
    return divs, primes
