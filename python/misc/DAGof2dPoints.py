# https://atcoder.jp/contests/arc200/submissions/66899857

"""
2 次元平面上の点について、(x[i] <= x[j] かつ y[i] <= y[j] なら辺 ij を張る)というDAG を考える
この関数は、補助頂点を使って O(N log N) 本の辺からなる DAG を作る
（注: 不等号の向きは x_reverse, y_reverse で指定可能）
"""
def DAGof2dPoints(points, x_reverse, y_reverse):
    def solveDC(l,r):
        # return list of index + (flag of is_R), sorted by key=lambda i:Y[i], reverse = y_reverse
        nonlocal g
        if l+1 == r:
            i = X[l]&((1<<20)-1)
            return [Y[i]*2]

        m = (l+r)//2
        Ys = [i&(~1) for i in solveDC(l,m)] + [i|1 for i in solveDC(m,r)]
        Ys.sort(reverse=y_reverse)
        
        offset = len(g)
        for i in range(len(Ys)-1):
            g.append([offset+i+1])
        g.append([])
        
        for i,y_info in enumerate(Ys):
            is_R = y_info&1
            idx = (y_info>>1)&((1<<20)-1)
            if is_R:
                g[offset+i].append(idx)
            else:
                g[idx].append(offset+i)
        return Ys

    n = len(points)
    assert n < (1<<20)
    X = [0]*n
    Y = [0]*n
    for i,point in enumerate(points):
        X[i] = (point[0]<<20) + i
        Y[i] = (point[1]<<20) + i
    X.sort(reverse=x_reverse)
    
    g = [[] for _ in range(n)]
    solveDC(0,n)
    return g
