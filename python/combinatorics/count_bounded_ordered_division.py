# competitive-verifier: TITLE 長さ K 以下のブロックで合計長 N を作る場合の数

pow2 = [1]*(SIZE+1)
for i in range(1,SIZE+1):
    pow2[i] = pow2[i-1]*2%MOD

def count_bounded_ordered_division(N, K):
    """
    長さ 1 以上 K 以下のブロックで、合計長 N を作る場合の数
    計算量: O(N/(K+1))
    """
    if N == 0:
        return 1
    if N < 0 or K <= 0:
        return 0
    # 長さ制限が実質ない場合、N を正のブロック列に分ける方法は 2**(N-1)
    if K >= N:
        return pow2[N - 1]

    ans = 0
    for i in range(N//(K+1) + 1):
        m = N - (K+1)*i
        # [x^N] (1-x) / (1-2x+x^{K+1}) = [x^N] sum_i (-1)^i x^{(K+1)i}(1-x)/(1-2x)^{i+1}
        term = pow2[m] * choose(m + i, i) % MOD
        if m >= 1:
            term -= pow2[m - 1] * choose(m - 1 + i, i) % MOD
        ans = (ans + (-term if i&1 else term)) % MOD

    return ans % MOD


# MOD はグローバル変数

def count_bounded_ordered_division_fixed_K(N, K):
    """
    dp[n] = count_bounded_ordered_division(n, K) を、n <= N で計算
    """

    dp = [0] * (N + 1)
    dp[0] = 1

    if K <= 0: return dp

    s = 0
    for n in range(1, N + 1):
        # dp[n] = dp[n-1] + dp[n-2] + ... + dp[n-K]
        s += dp[n - 1]
        if n - K - 1 >= 0:
            s -= dp[n - K - 1]
        s %= MOD
        dp[n] = s
    
    return dp

# https://atcoder.jp/contests/abc456/submissions/75784969


