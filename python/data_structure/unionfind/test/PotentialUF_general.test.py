# verification-helper: PROBLEM https://judge.yosupo.jp/problem/unionfind_with_potential_non_commutative_group

from python.data_structure.unionfind.PotentialUnionFindGeneral import PotentialUnionFindGeneral
import sys
readline = sys.stdin.readline

def main():
    n,Q = map(int,readline().split())
    MOD = 998244353
    
    def mul(x,y):
        a,b,c,d = x
        p,q,r,s = y
        return ((a*p+b*r)%MOD,(a*q+b*s)%MOD,(c*p+d*r)%MOD,(c*q+d*s)%MOD)
    
    def inv(x):
        return (x[3],(-x[1])%MOD,(-x[2])%MOD,x[0])
    
    UF = PotentialUnionFindGeneral(n,mul,inv,(1,0,0,1))
    for _ in range(Q):
        t,*lst = list(map(int,readline().split()))
        if t == 0:
            u,v,*x = lst
            x = tuple(x)
            if UF.issame(u,v):
                d = UF.diff(u,v)
                if d!=x:
                    print(0)
                    continue
            UF.merge(u,v,x)
            print(1)
        else:
            u,v = lst
            if UF.issame(u,v):
                d = UF.diff(u,v)
                print(*d)
            else:
                print(-1)
    

if __name__ == '__main__':
    main()

