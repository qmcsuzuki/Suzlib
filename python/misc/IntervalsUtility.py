# competitive-verifier: TITLE 区間ユーティリティ

# find 系: https://atcoder.jp/contests/arc190/submissions/61691736

from python.data_structure.SortedMultiset import SortedMultiset


class IntervalsUtility:
    """空でない半開区間 [l,r) の列を扱う。座標は整数。"""
    def __init__(self,LR):
        """非空の半開整数区間の列を保存し、区間数を設定する。"""
        self.n = len(LR)
        self.LRI = [(*lst,i) for i,lst in enumerate(LR)]
        self.L, self.R = zip(*LR) if LR else ((), ())

    def find_non_overlapping_pair(self):
        """
        return (i,j) with [Li,Ri) ∩ [Lj,Rj) = empty
        return (-1,-1) if no such intervals
        """
        if self.n < 2: return (-1,-1)
        lmax, rmin, ridx = self.LRI[0]
        lidx = ridx
        for l,r,i in self.LRI:
            if rmin > r: rmin = r; ridx = i
            if lmax < l: lmax = l; lidx = i
        return (ridx,lidx) if rmin <= lmax else (-1,-1)

    def find_including_pair(self):
        """
        return (i,j) with [Li,Ri) ⊆ [Lj,Rj)
        return (-1,-1) if no such intervals
        """
        pi = -1
        pr = None
        for l,r,i in sorted(self.LRI, key=lambda x: (x[0], -x[1])):
            if pr is not None and r <= pr:
                return i,pi
            pi, pr = i, r
        return (-1,-1)

    def count_non_overlapping_intervals(self):
        """
        return res: list[int], where res[i] = #{j | LR[i] ∩ LR[j] = empty}
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


def intervals_including(LRI):
    """
    count j with [lj,rj) ⊆ [li,ri) for each i
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
    count j with [li,ri) ⊆ [lj,rj) for each i
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
