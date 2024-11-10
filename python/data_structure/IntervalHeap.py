"""
double ended priority queue
"""
class IntervalHeap:
    def __init__(self):
        self.data = []

    def __len__(self):
        return len(self.data)
    
    def __str__(self):
        return f"minheap: {self.data[::2]}, maxheap: {self.data[1::2]}"

    def heappush(self, v: int):
        self.data.append(v)
        L = len(self.data)
        if L%2 == 0:
            if v < self.data[-2]:
                self.data[L-1], self.data[L-2] = self.data[L-2],self.data[L-1]
                self._shift_up_min(L-2)
            else:
                self._shift_up_max(L-1)
        else:
            self._shift_up_min(L-1)
            if v == self.data[-1]:
                self._shift_up_max(L-1)

    def pop_min(self):
        if len(self.data) <= 2:
            return self.data.pop(0)
        res = self.data[0]
        self.data[0] = self.data[-1]
        self.data.pop()
        self._shift_down_min(0)
        return res

    def pop_max(self):
        if len(self.data) <= 2:
            return self.data.pop()
        res = self.data[1]
        self.data[1] = self.data[-1]
        self.data.pop()
        self._shift_down_max(1)
        return res

    def get_min(self):
        return self.data[0]

    def get_max(self):
        return self.data[0] if len(self.data)==1 else self.data[1]

    def _shift_up_min(self, idx: int):
        while idx:
            par = (idx//2-1) & (~1)
            if self.data[idx] < self.data[par]:
                self.data[idx], self.data[par] = self.data[par], self.data[idx]
                idx = par
            else:
                return

    def _shift_up_max(self, idx: int):
        while idx > 1:
            par = (idx//2-1) | 1
            if self.data[idx] > self.data[par]:
                self.data[idx], self.data[par] = self.data[par], self.data[idx]
                idx = par
            else:
                return

    def _shift_down_min(self, idx: int):
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

    def _shift_down_max(self, idx: int):
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
