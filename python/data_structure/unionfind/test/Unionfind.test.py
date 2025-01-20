# verification-helper: PROBLEM https://judge.yosupo.jp/problem/unionfind

from python.data_structure.unionfind.Unionfind import Unionfind
import sys
readline = sys.stdin.readline

def main():    
    N,Q = map(int,readline().split())    
    uf = Unionfind(N)
    
    for _ in range(Q):
        t,u,v = map(int,readline().split())
        if t == 0:
            uf.merge(u, v)
        else:
            print("1" if uf.issame(u,v) else "0")

if __name__ == '__main__':
    main()
