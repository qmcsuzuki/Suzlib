class SparseTable:
    def __init__(self, a, op):
        self.op = op
        self.table = [a[:]]
        n = len(a)
        r = 1 #区間の幅の半分
        T = self.table[-1]
        while 2*r <= n:
            self.table.append(T := [op(T[i],T[i+r]) for i in range(len(T)-r)])
            r *= 2

    """
    /**
    * @brief 半開区間 [L,R) 上の区間積を返す
    * @param[in] a(引数名) 引数の説明
    * @param[out] b(引数名) 引数の説明
    * @return bool 戻り値の説明
    * @details 詳細な説明
    */
    """
    def prod(self, L,R):
        assert L < R
        i = (R-L).bit_length()-1 #2**i <= R-L < 2**(i+1)
        return self.op(self.table[i][L], self.table[i][R-(1<<i)])


