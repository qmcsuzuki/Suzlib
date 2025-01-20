# verification-helper: PROBLEM https://judge.yosupo.jp/problem/unionfind_with_potential

from python.data_structure.unionfind.PotentialUnionFind import PotentialUnionFind
import sys
readline = sys.stdin.readline

def main():
    n,Q = map(int,readline().split())
    MOD = 998244353
    
    UF = PotentialUnionFind(n)
    for _ in range(Q):
        t,*lst = list(map(int,readline().split()))
        if t == 0:
            u,v,x = lst
            if UF.issame(u,v):
                d = UF.diff(v,u)
                if (d-x)%MOD:
                    print(0)
                    continue
            UF.merge(v,u,x)
            print(1)
        else:
            u,v = lst
            if UF.issame(u,v):
                d = UF.diff(v,u)
                print(d%MOD)
            else:
                print(-1)
    

if __name__ == '__main__':
    main()

