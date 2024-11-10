# verification-helper: PROBLEM https://judge.yosupo.jp/problem/double_ended_priority_queue

from data_structure.IntervalHeap import *
import sys
readline = sys.stdin.readline

def main():
    n,Q = map(int,readline().split())
    *S, = map(int,readline().split())
    
    q = IntervalHeap()
    for i in S:
        q.heappush(i)
    
    for _ in range(Q):
        t,*lst = map(int,readline().split())
        if t==0:
            q.heappush(lst[0])
        elif t==1:
            print(q.pop_min())
        elif t==2:
            print(q.pop_max())

if __name__ == '__main__':
    main()
