# competitive-verifier: TITLE 上位 K 個の和を求める/median の管理

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
    """要素の追加・削除に対応し、大きい方から K 個の和を管理する。"""
    def __init__(self, K, initial = None):
        """初期要素を上位 K 個と残りに分け、それぞれのヒープを構築する。"""
        self.K = K
        initial = [] if initial is None else list(initial)
        initial.sort(reverse=1)
        self.q_topK = DeletableHeapqInt(initial[:K])
        self.q_other = DeletableHeapqInt([-x for x in initial[K:]])
    
    def __str__(self):
        """現在の内容を表示用文字列に変換する。"""
        return f"***top K***\n{self.q_topK}\n***other(need mul -1)***\n{self.q_other}"

    def get_topK(self):
        """大きい方から K 個の要素の和を返す。"""
        return self.q_topK.sum

    def get_other(self):
        """上位 K 個に含まれない要素の和を返す。"""
        return -self.q_other.sum
    
    def add(self,v):
        """値 v を追加し、上位 K 個の区分を保つ。"""
        self.q_topK.heappush(v)
        if len(self.q_topK) > self.K:
            x = self.q_topK.heappop()
            self.q_other.heappush(-x)

    def remove(self,v):
        """存在する値 v を一つ削除し、上位 K 個の区分を保つ。"""
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
        """K を 1 増やし、必要なら要素を上位側に移す。"""
        self.K += 1
        if len(self.q_other):
            x = -self.q_other.heappop()
            self.q_topK.heappush(x)

    def minus_K(self):
        """K を 1 減らし、必要なら要素を下位側に移す。"""
        self.K -= 1
        assert self.K >= 0
        if len(self.q_topK) > self.K:
            x = self.q_topK.heappop()
            self.q_other.heappush(-x)

# https://atcoder.jp/contests/arc196/submissions/64599110

# Specialized for Median maintenance:
# add, remove, get upper/lower median
class MedianMaintainer(TopKSum):
    """要素の追加・削除に対応し、上下の中央値を管理する。"""
    def __init__(self, initial = None):
        """初期要素数に合わせて上下の中央値を取得できる二つのヒープを構築する。"""
        initial = [] if initial is None else list(initial)
        self.n = len(initial)
        super().__init__((self.n + 1) // 2, initial)

    def add(self, v):
        """値 v を追加し、中央値を保つように上下の要素数を調整する。"""
        super().add(v)
        self.n += 1
        if (self.n + 1) // 2 > self.K:
            self.add_K()

    def remove(self, v):
        """存在する値 v を一つ削除し、中央値を保つように上下の要素数を調整する。"""
        super().remove(v)
        self.n -= 1
        if (self.n + 1) // 2 < self.K:
            self.minus_K()

    def get_upper_median(self):
        """要素数が偶数なら大きい側の中央値を返す。"""
        assert self.n > 0
        return self.q_topK.top()

    def get_lower_median(self):
        """要素数が偶数なら小さい側の中央値を返す。"""
        assert self.n > 0
        if self.n % 2 == 1:
            return self.q_topK.top()
        return -self.q_other.top()

"""
- https://atcoder.jp/contests/abc127/submissions/72270899
- https://atcoder.jp/contests/awc0055/submissions/75345247
"""
