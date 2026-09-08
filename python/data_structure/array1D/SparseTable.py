# competitive-verifier: TITLE スパーステーブル (Sparse Table)

class SparseTable:
    """冪等かつ結合的な演算の静的な区間積を定数時間で求める。"""
    def __init__(self, a, op):
        """初期列 a と冪等な結合演算 op からスパーステーブルを構築する。"""
        self.op = op
        self.table = [T := a[:]]
        n = len(a)
        r = 1 #区間の幅の半分
        while 2*r <= n:
            self.table.append(T := [op(T[i],T[i+r]) for i in range(len(T)-r)])
            r *= 2

    # 半開区間 [L,R) 上の区間積を返す
    def prod(self, L,R):
        """非空の半開区間 [L,R) の積を冪等演算で求める。"""
        assert L < R
        i = (R-L).bit_length()-1 #2**i <= R-L < 2**(i+1)
        return self.op(self.table[i][L], self.table[i][R-(1<<i)])

###############################################

# argmin or argmax を扱うもの
class SparseTableArgminmax(SparseTable):
    """区間の最小値または最大値とその添字を求めるスパーステーブル。"""
    M = 1<<20
    def __init__(self, a, min_or_max):
        """値と添字を符号化し、min または max のスパーステーブルを構築する。"""
        aa = [v*self.M+i for i,v in enumerate(a)]
        super().__init__(aa, min_or_max)
    
    # 値、添え字のペアを返す
    def prod(self, L,R):
        """半開区間 [L,R) の極値と添字を返し、同値では min は左、max は右を優先する。"""
        return divmod(super().prod(L,R), self.M)

