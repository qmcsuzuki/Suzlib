# competitive-verifier: TITLE 削除可能ヒープ (Deletable Heapq)

from heapq import *
class DeletableHeapq:
    """
    削除可能heapq
    削除する元があることを仮定している（必要なときは別途 set や dict を持つ）
    """
    def __init__(self, initial = []):
        if initial:
            self.q = initial[::]
            heapify(self.q)
        else: self.q = []
        self.q_del = []

    def __len__(self):
        return len(self.q) - len(self.q_del)        
    
    def __str__(self):
        return f"queue:{self.q}" + "\n" + f"del:{self.q_del}"

    def propagate(self):
        while self.q_del and self.q[0] == self.q_del[0]:
            heappop(self.q)
            heappop(self.q_del)

    def heappop(self):
        self.propagate()
        return heappop(self.q)
    
    def top(self):
        self.propagate()
        return self.q[0]
            
    def remove(self,x):
        heappush(self.q_del,x)

    def heappush(self,x):
        heappush(self.q,x)

"""
要素が整数の場合、和も一緒に管理する特殊化
"""
class DeletableHeapqInt(DeletableHeapq):
    def __init__(self, initial = []):
        super().__init__(initial)
        self.sum = sum(initial)

    def heappop(self):
        self.propagate()
        x = heapq.heappop(self.q)
        self.sum -= x
        return x

    def remove(self,x):
        heapq.heappush(self.q_del,x)
        self.sum -= x

    def heappush(self,x):
        heapq.heappush(self.q,x)
        self.sum += x
