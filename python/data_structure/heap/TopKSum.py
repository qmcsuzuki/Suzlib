# competitive-verifier: TITLE 上位 K 個の和を求める

from python.data_structure.heap.DeletableHeapq import DeletableHeapqInt
"""
## 主なメソッド
- `get_topK()`：上位 K 個の要素の和を返す
- `get_other()`：上位 K 個以外の要素の和を返す
- `add(v)`：新しい要素 `v` を追加する
- `remove(v)`：要素 `v` を削除する
- `add_K()`：K の値を 1 増やす
- `minus_K()`：K の値を 1 減らす
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
        if len(self.q_topK) > self.K:
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
        if len(self.q_topK) > self.K:
            x = self.q_topK.heappop()
            self.q_other.heappush(-x)

# Median maintenance:
# upper median: a[(n+1)//2] (1-based) -> a[n//2] (0-based)
# lower median: a[(n+2)//2] (1-based) -> a[(n-1)//2] (0-based)
class MedianMaintainer(TopKSum):
    def __init__(self, initial = []):
        self.n = len(initial)
        super().__init__((self.n + 1) // 2, initial)

    def add(self, v):
        super().add(v)
        self.n += 1
        if (self.n + 1) // 2 > self.K:
            self.add_K()

    def remove(self, v):
        super().remove(v)
        self.n -= 1
        if (self.n + 1) // 2 < self.K:
            self.minus_K()

    def get_upper_median(self):
        assert self.n > 0
        return self.q_topK.top()

    def get_lower_median(self):
        assert self.n > 0
        if self.n % 2 == 1:
            return self.q_topK.top()
        return -self.q_other.top()

# https://atcoder.jp/contests/arc196/submissions/64599110
