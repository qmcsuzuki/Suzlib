# verification-helper: PROBLEM https://judge.yosupo.jp/problem/double_ended_priority_queue

from data_structure.DeletableHeapq import DeletableHeapq
import sys
readline = sys.stdin.readline

class MinMaxHeap:
    def __init__(self,init = []):
        self.q_min = DeletableHeapq(init)
        self.q_max = DeletableHeapq([-i for i in init])

    def __len__(self):
        return len(self.q_min)
    
    def __str__(self):
        return f"{self.q_min}"
    
    def heappush(self,v):
        self.q_min.heappush(v)
        self.q_max.heappush(-v)

    def get_min(self):
        print(self.q_min.top())

    def get_max(self):
        print(-self.q_max.top())

    def pop_min(self):
        v = self.q_min.heappop()
        self.q_max.remove(-v)
        return v

    def pop_max(self):
        v = -self.q_max.heappop()
        self.q_min.remove(v)
        return v

def main():
    n,Q = map(int,readline().split())
    *S, = map(int,readline().split())
    
    q = MinMaxHeap(S)

    for _ in range(Q):
        t,*lst = map(int,readline().split())
        #print(t,q)
        if t==0:
            q.heappush(lst[0])
        elif t==1:
            print(q.pop_min())
        elif t==2:
            print(q.pop_max())

if __name__ == '__main__':
    main()
