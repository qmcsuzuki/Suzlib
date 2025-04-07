# verification-helper: TITLE 上位 K 個の和を求める

from python.data_structure.heap.DeletableHeapq import DeletableHeapqInt
"""
top K の和を求める
"""
class TopKSum:
    def __init__(self, K, initial = []):
        self.K = K
        initial.sort(reverse=1)
        self.q_topK = DeletableHeapqInt(initial[:K])
        self.q_other = DeletableHeapqInt([-x for x in initial[K:]])
    
    def __str__(self):
        return f"***top K***\n{self.q_topK}\n***other(need mul -1)***\n{self.q_other}"

    def get_topK(self):
        return self.q_topK.sum

    def get_other(self):
        return -self.q_other.sum
    
    def add(self,v):
        self.q_topK.heappush(v)
        while len(self.q_topK) > self.K:
            x = self.q_topK.heappop()
            self.q_other.heappush(-x)

    def remove(self,v):
        if self.K == 0:
            self.q_other.remove(-v)
            return
        t = self.q_topK.top()
        if t <= v:
            self.q_topK.remove(v)
            if len(self.q_other):
                x = -self.q_other.heappop()
                self.q_topK.heappush(x)
        else:
            self.q_other.remove(-v)

    def add_K(self):
        self.K += 1
        if len(self.q_other):
            x = -self.q_other.heappop()
            self.q_topK.heappush(x)

    def minus_K(self):
        self.K -= 1
        assert self.K >= 0
        if len(self.q_topK):
            x = self.q_topK.heappop()
            self.q_other.heappush(-x)

# https://atcoder.jp/contests/arc196/submissions/64599110
