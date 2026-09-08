# competitive-verifier: TITLE Sliding window aggregation (SWAG)

from collections import deque
class SWAG:
    """列の末尾追加・先頭削除とモノイドによる全体集約を行う。"""
    def __init__(self, operator_M, e_M, init=None):
        """集約演算と単位元を設定し、初期列から左右の集約列を構築する。"""
        self.op_M = operator_M
        self.e_M = e_M
        self.accL = [e_M]
        self.accR = e_M
        self.L = self.R = 0
        if init is None:
            self.q = deque()
        else:
            self.q = deque(init)
            self.L = len(init)
            for i in reversed(init):
                self.accL.append(self.op_M(i, self.accL[-1]))

    def __len__(self):
        """格納されている要素の個数を返す。"""
        return self.L + self.R

    def fold_all(self):
        """キューの全要素を先頭から順に演算で集約して返す。"""
        return self.op_M(self.accL[-1],self.accR)

    def append(self,x):
        """値を末尾に追加し、集約値を更新する。"""
        self.q.append(x)
        self.accR = self.op_M(self.accR,x)
        self.R += 1
    
    def popleft(self):
        """先頭要素を削除して返し、必要なら左右の集約列を組み直す。"""
        if self.L:
            self.accL.pop()
            self.L -= 1
            return self.q.popleft()
        elif self.R:
            v = self.q.popleft()
            self.L,self.R = self.R-1,0
            for i in reversed(self.q):
                self.accL.append(self.op_M(i,self.accL[-1]))
            self.accR = self.e_M
            return v
        else:
            assert 0
