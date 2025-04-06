# verification-helper: PROBLEM https://onlinejudge.u-aizu.ac.jp/courses/lesson/8/ITP2/2/ITP2_2_C

from python.data_structure.heap.BinaryHeap import BinaryHeap
import sys
readline = sys.stdin.readline

def main():
    n,Q = map(int,readline().split())
    q = [BinaryHeap([],lambda x:-x) for _ in range(n)]
    for _ in range(Q):
        t,i,*lst = map(int,readline().split())
        if t==0:
            q[i].heappush(lst[0])
        elif t==1:
            if q[i]: print(q[i].top())
        else:
            if q[i]: q[i].heappop()

if __name__ == '__main__':
    main()
