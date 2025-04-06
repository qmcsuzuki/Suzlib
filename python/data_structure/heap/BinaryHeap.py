"""
general min heap, we can set "key" function
"""
class BinaryHeap:
    def __init__(self, init=None, key=lambda x:x):
        self.key = key
        if init is not None:
            self.data = init[::]
            self.heapify()
        else:
            self.data: list = []

    def __len__(self):
        return len(self.data)
    
    def __str__(self):
        return f"data: {self.data}"
    
    def heappush(self, v: int):
        self.data.append(v)
        self._sift_up(len(self.data)-1)

    def heappop(self):
        res = self.data[0]
        self.data[0] = self.data[-1]
        self.data.pop()
        self._sift_down(0)
        return res

    def top(self):
        return self.data[0]

    def _sift_up(self, idx: int):
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
        for i in range((len(self.data)-1)//2+1)[::-1]:
            self._sift_down(i)
