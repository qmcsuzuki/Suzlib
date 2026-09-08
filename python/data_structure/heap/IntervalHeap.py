# competitive-verifier: TITLE 区間ヒープ (Interval Heap)

"""
double ended priority queue
"""
class IntervalHeap:
    """最小値と最大値を取得・削除できる両端ヒープ。"""
    def __init__(self):
        """最小値側と最大値側を同時に管理する空のヒープを作る。"""
        self.data = []

    def __len__(self):
        """格納されている要素の個数を返す。"""
        return len(self.data)
    
    def __str__(self):
        """現在の内容を表示用文字列に変換する。"""
        return f"minheap: {self.data[::2]}, maxheap: {self.data[1::2]}"

    def heappush(self, v: int):
        """値をヒープに追加する。"""
        self.data.append(v)
        L = len(self.data)
        if L%2 == 0:
            if v < self.data[-2]:
                self.data[L-1], self.data[L-2] = self.data[L-2],self.data[L-1]
                self._sift_up_min(L-2)
            else:
                self._sift_up_max(L-1)
        else:
            self._sift_up_min(L-1)
            if v == self.data[-1]:
                self._sift_up_max(L-1)

    def pop_min(self):
        """最小の要素を取り除いて返す。"""
        if len(self.data) <= 2:
            return self.data.pop(0)
        res = self.data[0]
        self.data[0] = self.data[-1]
        self.data.pop()
        self._sift_down_min(0)
        return res

    def pop_max(self):
        """最大の要素を取り除いて返す。"""
        if len(self.data) <= 2:
            return self.data.pop()
        res = self.data[1]
        self.data[1] = self.data[-1]
        self.data.pop()
        self._sift_down_max(1)
        return res

    def get_min(self):
        """最小の要素を削除せずに返す。"""
        return self.data[0]

    def get_max(self):
        """最大の要素を削除せずに返す。"""
        return self.data[0] if len(self.data)==1 else self.data[1]

    def _sift_up_min(self, idx: int):
        """最小値側のノードを上へ移動してヒープ条件を回復する。"""
        while idx:
            par = (idx//2-1) & (~1)
            if self.data[idx] < self.data[par]:
                self.data[idx], self.data[par] = self.data[par], self.data[idx]
                idx = par
            else:
                return

    def _sift_up_max(self, idx: int):
        """最大値側のノードを上へ移動してヒープ条件を回復する。"""
        while idx > 1:
            par = (idx//2-1) | 1
            if self.data[idx] > self.data[par]:
                self.data[idx], self.data[par] = self.data[par], self.data[idx]
                idx = par
            else:
                return

    def _sift_down_min(self, idx: int):
        """最小値側のノードを下へ移動してヒープ条件を回復する。"""
        L = len(self.data)
        while idx*2+2 < L:
            c1 = idx*2+2
            c2 = c1+2
            nxt = c2 if c2 < L and self.data[c1] > self.data[c2] else c1
            if self.data[idx] <= self.data[nxt]:
                return
            self.data[idx],self.data[nxt] = self.data[nxt],self.data[idx]
            idx = nxt
            if idx+1 < L and self.data[idx] > self.data[idx+1]:
                self.data[idx], self.data[idx+1] = self.data[idx+1], self.data[idx]

    def _sift_down_max(self, idx: int):
        """最大値側のノードを下へ移動してヒープ条件を回復する。"""
        L = len(self.data)
        while idx*2+1 < L:
            c1 = idx*2+1
            c2 = c1+2
            nxt = c2 if c2 < L and self.data[c1] < self.data[c2] else c1
            if self.data[idx] >= self.data[nxt]:
                return
            self.data[idx],self.data[nxt] = self.data[nxt],self.data[idx]
            idx = nxt
            if idx-1 < L and self.data[idx-1] > self.data[idx]:
                self.data[idx-1], self.data[idx] = self.data[idx], self.data[idx-1]
