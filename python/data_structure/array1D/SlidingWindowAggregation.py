# verification-helper: TITLE スライディングウィンドウ集約 (SWAG)

from collections import deque
class SWAG:
    def __init__(self, operator_M, e_M):
        self.op_M = operator_M
        self.e_M = e_M
        self.q = deque([])
        self.accL = [e_M]
        self.accR = e_M
        self.L = self.R = 0

    def build(self,lst):
        self.q = deque(lst)
        self.L = len(lst)
        for i in reversed(lst):
            self.accL.append(self.op_M(i,self.acc[-1]))

    def __len__(self):
        return self.L + self.R

    def fold_all(self):
        return self.op_M(self.accL[-1],self.accR)

    def append(self,x):
        self.q.append(x)
        self.accR = self.op_M(self.accR,x)
        self.R += 1
    
    def popleft(self):
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
