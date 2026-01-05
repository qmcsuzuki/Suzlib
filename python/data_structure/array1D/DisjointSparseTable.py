# verification-helper: TITLE Disjoint Sparse Table

class DisjointSparseTable():
    def __init__(self, a:list, op):
        self.op = op
        self.data = [a[:]]
        n = len(a)
        step = 2
        while step < n:
            d = a[:]
            M = step
            while M < n:
                for k in range(M-step, M-1)[::-1]:
                    d[k] = op(d[k],d[k+1])
                for k in range(M+1, min(M+step,n)):
                    d[k] = op(d[k-1],d[k])
                M += step*2
            step *= 2
            self.data.append(d)

    #半開区間 [L,R) 上の区間積を返す
    def prod(self,l,r): # [l,r)
        r -= 1
        if l == r:
            return self.data[0][l]
        d = self.data[(l^r).bit_length()-1]
        return self.op(d[l],d[r])
