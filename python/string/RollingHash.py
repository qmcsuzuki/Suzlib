# competitive-verifier: TITLE ローリングハッシュ
MOD61 = (1<<61)-1

# a * b % MOD61 を計算
def mul_mod61(a, b):
    au, ad = divmod(a, 1<<31)
    bu, bd = divmod(b, 1<<31)
    midu, midd = divmod(ad * bu + au * bd, 1<<30)

    x = au * bu * 2 + midu + (midd << 31) + ad * bd
    x = (x >> 61) + (x & MOD61)
    return x if x < MOD61 else x - MOD61

class RollingHash61:
    MOD = MOD61
    BASE = 911382323 # 必要なら乱数にする
    powers = [1]
    
    @classmethod
    def _ensure_power(cls, n):
        L = len(cls.powers)
        if L > n: return
        powers = cls.powers
        
        powers += [0] * (n + 1 - L)
        for i in range(L, n + 1):
            powers[i] = mul_mod61(powers[i - 1], cls.BASE)

    def __init__(self, s):
        # 文字列・bytes・小さい非負整数列を想定
        if type(s) == str:
            S = list(map(ord, s))
        else:
            S = list(s)

        self.n = n = len(S)
        self.S = S
        self._ensure_power(n+1)
        self.h = h = [0]*(n+1)
        for i,x in enumerate(S):
            # hash に 0 を入れないように、各値に +1 して使う
            v = mul_mod61(h[i], self.BASE) + x + 1
            h[i + 1] = v if v < MOD61 else v - MOD61

    def get(self, l, r):
        # hash(S[l:r]) の値を返す
        x = self.h[r] - mul_mod61(self.h[l], self.powers[r - l])
        return x if x >= 0 else x + MOD61
    
    def is_same(self, l1, r1, other, l2, r2):
        # 文字列の一致判定
        return r1 - l1 == r2 - l2 and self.get(l1, r1) == other.get(l2, r2)

    # Longest Common Prefix: 先頭何文字が同じ？その数を返す
    def common_prefix_length(self, l1, r1, other, l2, r2):
        ok = 0
        ng = min(r1 - l1, r2 - l2) + 1
        while ng - ok > 1:
            mid = (ok + ng) // 2
            if self.get(l1, l1 + mid) == other.get(l2, l2 + mid):
                ok = mid
            else:
                ng = mid
        return ok

    # Longest Common Prefix: 末尾何文字が同じ？その数を返す
    def common_suffix_length(self, l1, r1, other, l2, r2):
        ok = 0
        ng = min(r1 - l1, r2 - l2) + 1
        while ng - ok > 1:
            mid = (ok + ng) // 2
            if self.get(r1 - mid, r1) == other.get(r2 - mid, r2):
                ok = mid
            else:
                ng = mid
        return ok
    
    # S1[l1:r1] と S2[l2:r2] でどちらが辞書順で小さいか
    # 返り値:
    #   -1 : S1[l1:r1] <  S2[l2:r2]
    #    0 : S1[l1:r1] == S2[l2:r2]
    #    1 : S1[l1:r1] >  S2[l2:r2]
    def compare(self, l1, r1, other, l2, r2):
        L = self.common_prefix_length(l1, r1, other, l2, r2)

        n1 = r1 - l1
        n2 = r2 - l2

        if L == min(n1, n2):
            return (n1 > n2) - (n1 < n2)

        a = self.S[l1 + L]
        b = other.S[l2 + L]
        return (a > b) - (a < b)

    @classmethod
    def concat_hash(cls, ha, hb, lb):
        # ハッシュ値単体の結合（la は使わない）
        # hash(A B) = hash(A) * BASE^|B| + hash(B)
        cls._ensure_power(lb)
        v = mul_mod61(ha, cls.powers[lb]) + hb
        return v if v < MOD61 else v-MOD61

    @classmethod
    def concat_pairs(cls, a, b):
        ha, la = a
        hb, lb = b
        return (cls.concat_hash(ha, hb, lb), la + lb)

