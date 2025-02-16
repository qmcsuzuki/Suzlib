# verification-helper: TITLE スパーステーブル (Sparse Table)

class SparseTable:
    def __init__(self, a, op):
        self.op = op
        self.table = [T := a[:]]
        n = len(a)
        r = 1 #区間の幅の半分
        while 2*r <= n:
            self.table.append(T := [op(T[i],T[i+r]) for i in range(len(T)-r)])
            r *= 2

    # 半開区間 [L,R) 上の区間積を返す
    def prod(self, L,R):
        assert L < R
        i = (R-L).bit_length()-1 #2**i <= R-L < 2**(i+1)
        return self.op(self.table[i][L], self.table[i][R-(1<<i)])

###############################################

# argmin or argmax を扱うもの
class SparseTableArgminmax(SparseTable):
    M = 1<<20
    def __init__(self, a, min_or_max):
        aa = [v*self.M+i for i,v in enumerate(a)]
        super().__init__(aa, min_or_max)
    
    # 値、添え字のペアを返す
    def prod(self, L,R):
        return divmod(super().prod(L,R), self.M)

