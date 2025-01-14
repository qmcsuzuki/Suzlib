class IntervalsUtility:
    def __init__(self,LR):
        self.n = len(LR)
        self.LRI = [(*lst,i) for i,lst in enumerate(LR)]
        self.L, self.R = zip(*LR)

    def find_non_overlapping_pair(self):
        """
        return (i,j) with [Li,Ri) \cap [Lj,Rj) = empty
        return (-1,-1) if no such intervals
        """
        rmin = ridx = self.LRI[0][1]+1 # = r0
        lmax = lidx = -1
        for l,r,i in self.LRI:
            if rmin > r: rmin = r; ridx = i
            if lmax < l: lmax = l; lidx = i
        return (ridx,lidx) if rmin <= lmax else (-1,-1)

    def find_including_pair(self):
        """
        return (i,j) with [Li,Ri) \subset [Lj,Rj)
        return (-1,-1) if no such intervals
        """
        pi = pl = pr = -1
        for i in sorted(list(range(self.n)), key=lambda i: (self.LRI[i][0]<<30)-self.LRI[i][1]):
            l,r = LR[i]
            if r <= pr: # [l,r) \usbset [pl,pr)
                return i,pi
            else:
                pi = i
                pl = l
                pr = r
        return (-1,-1)

    def count_non_overlapping_intervals(self):
        """
        return res: list[int], where res[i] = #{j | LR[i] \cap LR[j] = empty}
        """
        n = len(self.LRI)
        events = [] # (position, is_l, index)
        for l,r,i in self.LRI:
            events.append((2*l+1)*n+i)
            events.append((2*r+0)*n+i)
        events.sort()
        # count j with R[j] <= L[i] for each i
        res = [0]*n
        c = 0
        for v in events:
            if (v//n)&1: res[v%n] += c # l
            else: c += 1 # r
        # count j with R[i] <= L[j] for each i
        c = 0
        for v in events[::-1]:
            if (v//n)&1: c += 1 # l
            else: res[v%n] += c # r
        return res







# debug
# find 系: https://atcoder.jp/contests/arc190/submissions/61691736
# count non overlapping

def brute_non_overlapping(LR):
    n = len(LR)
    res = [0]*n
    for i in range(n):
        l1,r1 = LR[i]
        for j in range(n):
            if i==j: continue
            l2,r2 = LR[j]
            if r1 <= l2 or r2 <= l1:
                res[i] += 1
    return res

##########
from random import randrange
def random_intervals(n,M):
    LR = []#,LRI = [],[]
    for i in range(n):
        l = randrange(M-1)
        r = randrange(l+1,M)
        LR.append([l,r])
        #LRI.append([l,r,i])
    return LR#,LRI

def test_non_overlapping(T,n,M):
    for _ in range(T):
        LR = random_intervals(n,M)
        util = IntervalsUtility(LR)
        r1 = util.count_non_overlapping_intervals()
        r2 = brute_non_overlapping(LR)
        assert r1==r2

for T,n,M in [(100,3,3),(100,100,200),(100,100,10)]:
    test_non_overlapping(T,n,M)
    LR = random_intervals(n=5*10**4,M=10**9)
    util = IntervalsUtility(LR)
    r1 = util.count_non_overlapping_intervals()

#################################################
sortedmultiset を使った実装
def intervals_including(LRI):
    """
    count j with [lj,rj) \subset [li,ri) for each i
    """
    n = len(LRI)
    res = [0]*n

    s = SortedMultiset()
    LRI.sort(key=lambda x:x[1])
    LRI.sort(key=lambda x:-x[0])
    pl = pr = -1
    q = []
    for l,r,i in LRI:
        if pl == l and pr == r:
            q.append(i)
        else:
            for j in q: # consider the same intervals
                res[j] += len(q)-1
                s.add(pr)
            q = [i]
            pl = l
            pr = r
        res[i] += s.index_right(r)
    for j in q:
        res[j] += len(q)-1
    return res

def intervals_included_by(LRI):
    """
    count j with [li,ri) \subset [lj,rj) for each i
    """
    n = len(LRI)
    res = [0]*n

    s = SortedMultiset()
    LRI.sort(key=lambda x:x[0])
    LRI.sort(key=lambda x:-x[1])
    pl = pr = -1
    q = []
    for l,r,i in LRI:
        if pl == l and pr == r:
            q.append(i)
        else:
            for j in q: # consider the same intervals
                res[j] += len(q)-1
                s.add(pl)
            q = [i]
            pl = l
            pr = r
        res[i] += s.index_right(l)
    for j in q:
        res[j] += len(q)-1
    return res

def brute_non_overlapping(LRI):
    n = len(LRI)
    res = [0]*n
    for i in range(n):
        l1,r1,_ = LRI[i]
        for j in range(n):
            if i==j: continue
            l2,r2,_ = LRI[j]
            if r1 <= l2 or r2 <= l1:
                res[i] += 1
    return res

def brute_including(LRI):
    n = len(LRI)
    res = [0]*n
    for i in range(n):
        l1,r1,_ = LRI[i]
        for j in range(n):
            if i==j: continue
            l2,r2,_ = LRI[j]
            if l1 <= l2 and r2 <= r1:
                res[i] += 1
    return res

def brute_included_by(LRI):
    n = len(LRI)
    res = [0]*n
    for i in range(n):
        l1,r1,_ = LRI[i]
        for j in range(n):
            if i==j: continue
            l2,r2,_ = LRI[j]
            if l2 <= l1 and r1 <= r2:
                res[i] += 1
    return res

##########
from random import randrange
def random_intervals(n,M):
    LRI = []
    for i in range(n):
        l = randrange(M-1)
        r = randrange(l+1,M)
        LRI.append([l,r,i])
    return LRI

def test_non_overlapping(T,n,M):
    for _ in range(T):
        LRI = random_intervals(n,M)        
        r1 = brute_non_overlapping(LRI)
        r2 = intervals_non_overlapping(LRI)
        assert r1==r2

def test_including(T,n,M):
    for _ in range(T):
        LRI = random_intervals(n,M)        
        r1 = brute_including(LRI)
        r2 = intervals_including(LRI)
        assert r1==r2

def test_included_by(T,n,M):
    for _ in range(T):
        LRI = random_intervals(n,M)        
        r1 = brute_included_by(LRI)
        r2 = intervals_included_by(LRI)
        assert r1==r2

for T,n,M in [(100,100,200),(100,100,10)]:
    test_non_overlapping(T,n,M)
    test_including(T,n,M)
    test_included_by(T,n,M)

LRI = random_intervals(n=5*10**4,M=10**9)
r = intervals_non_overlapping(LRI)
r = intervals_including(LRI)
r = intervals_included_by(LRI)


