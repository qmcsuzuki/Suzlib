# competitive-verifier: TITLE [x^N] 1/(1 + A x^B + C x^D) (3 項多項式の逆数の係数 O(N/D))

def coeff_inv_three_terms(N, B, D, powAneg, powCneg):
    """
    [x^N] 1 / (1 + A x^B + C x^D) を O(N/D) で求める

    powAneg[q] = (-A)^q
    powCneg[i] = (-C)^i
    """
    if N < 0:
        return 0

    assert B >= 1 and D >= 1

    ans = 0
    for i in range(N // D + 1):
        m = N - D * i
        if m % B == 0:
            q = m // B
            ans = (ans + powCneg[i] * powAneg[q] % MOD * choose(q + i, i)) % MOD

    return ans
