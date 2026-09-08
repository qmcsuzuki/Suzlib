# competitive-verifier: TITLE 二分ヒープ (Binary Heap)

"""
general min heap, we can set "key" function
"""
class BinaryHeap:
    """key 関数の値が小さい要素を先頭に管理する二分ヒープ。"""
    def __init__(self, init=None, key=lambda x:x):
        """初期列を取り込み、key の値が小さい要素を優先するヒープを構築する。"""
        self.key = key
        if init is not None:
            self.data = init[::]
            self.heapify()
        else:
            self.data: list = []

    def __len__(self):
        """格納されている要素の個数を返す。"""
        return len(self.data)
    
    def __str__(self):
        """現在の内容を表示用文字列に変換する。"""
        return f"data: {self.data}"
    
    def heappush(self, v: int):
        """値をヒープに追加する。"""
        self.data.append(v)
        self._sift_up(len(self.data)-1)

    def heappop(self):
        """ヒープの先頭要素を取り除いて返す。"""
        res = self.data[0]
        self.data[0] = self.data[-1]
        self.data.pop()
        self._sift_down(0)
        return res

    def top(self):
        """ヒープの先頭要素を削除せずに返す。"""
        return self.data[0]

    def _sift_up(self, idx: int):
        """指定ノードを上へ移動してヒープ条件を回復する。"""
        key_idx = self.key(self.data[idx])
        while idx:
            par = (idx-1)//2
            key_par = self.key(self.data[par])
            if key_idx < self.key(self.data[par]):
                self.data[idx], self.data[par] = self.data[par], self.data[idx]
                idx = par
            else:
                return idx

    def _sift_down(self, idx: int):
        """指定ノードを下へ移動してヒープ条件を回復する。"""
        L = len(self.data)
        if not L: return
        keyvalue = self.key(self.data[idx])
        while idx*2+1 < L:
            c1 = idx*2+1
            c2 = c1+1
            nxt = c2 if c2 < L and self.key(self.data[c1]) > self.key(self.data[c2]) else c1
            if keyvalue < self.key(self.data[nxt]):
                return
            self.data[idx],self.data[nxt] = self.data[nxt],self.data[idx]
            idx = nxt

    def heapify(self):
        """内部配列全体をヒープ条件を満たすように並べ直す。"""
        for i in range((len(self.data)-1)//2+1)[::-1]:
            self._sift_down(i)
