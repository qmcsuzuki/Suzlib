# competitive-verifier: STANDALONE

from itertools import product

from python.misc.IntervalsUtility import IntervalsUtility, intervals_including, intervals_included_by


def check_intervals(LR):
    util = IntervalsUtility(LR)
    n = len(LR)
    disjoint = [(i,j) for i in range(n) for j in range(n) if i != j
                and (LR[i][1] <= LR[j][0] or LR[j][1] <= LR[i][0])]
    included = [(i,j) for i in range(n) for j in range(n) if i != j
                and LR[j][0] <= LR[i][0] and LR[i][1] <= LR[j][1]]
    for result, pairs in [(util.find_non_overlapping_pair(), disjoint),
                          (util.find_including_pair(), included)]:
        assert result in pairs if pairs else result == (-1,-1)
    assert util.count_non_overlapping_intervals() == [sum(i == k for i,j in disjoint) for k in range(n)]
    LRI = [(l,r,i) for i,(l,r) in enumerate(LR)]
    assert intervals_including(LRI[:]) == [sum(j == k for i,j in included) for k in range(n)]
    assert intervals_included_by(LRI[:]) == [sum(i == k for i,j in included) for k in range(n)]


if __name__ == "__main__":
    choices = [(l,r) for l in range(-2,3) for r in range(l+1,4)]
    for n in range(4):
        for LR in product(choices, repeat=n):
            check_intervals(list(LR))
    check_intervals([(0,1), (1,1 << 40), (-10,-5), (-10,-5)])
