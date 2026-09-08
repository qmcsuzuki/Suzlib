# competitive-verifier: TITLE 2次元点のDAG

# https://atcoder.jp/contests/arc165/submissions/66901191
# https://atcoder.jp/contests/arc200/submissions/66901173
"""
相異なる 2 次元平面上の点について、(i != j かつ x[i] <= x[j] かつ y[i] <= y[j] なら辺 ij を張る)という DAG を考える
同一点の重複は相互到達を要求して DAG と両立しないため禁止する。
空入力には [] を返す。先頭 N 頂点が入力の各点に対応する。
この関数は、補助頂点を使って O(N log N) 本の辺からなる DAG を作る
（注: 不等号の向きは x_reverse, y_reverse で指定可能）
"""
def DAGof2dPoints(points, x_reverse, y_reverse):
    """相異なる二次元点の座標比較による到達関係を、補助頂点付き DAG で表す。"""
    def solveDC(l,r):
        """x 順の区間を分割統治して辺を追加し、y 順の符号化頂点列を返す。"""
        # return sorted list of Y_coord*M + index
        nonlocal g
        if l+1 == r:
            return [Y[X[l]&((1<<20)-1)]]

        m = (l+r)//2
        Y2 = solveDC(m,r)
        offset = len(g)
        len_y2 = len(Y2)
        for i in range(len_y2-1):
            g.append([offset+i+1, Y2[i]&((1<<20)-1)])
        g.append([Y2[-1]&((1<<20)-1)])

        Y1 = solveDC(l,m)
        L = 0
        for y_info in Y1:
            y1,idx = divmod(y_info,1<<20)
            while L < len_y2 and ((not y_reverse and y1 > Y2[L]>>20) or
                                  (y_reverse and y1 < Y2[L]>>20)):
                L += 1
            if L == len_y2: break
            g[idx].append(offset+L)

        Y1 += Y2
        Y1.sort(reverse=y_reverse)
        return Y1
    
    n = len(points)
    assert n < (1<<20)
    if n == 0: return []
    X = [0]*n
    Y = [0]*n
    for i,point in enumerate(points):
        X[i] = (point[0]<<20) + i
        Y[i] = (point[1]<<20) + i
    # x が等しい点も、y の条件を満たす向きに並べる。
    X.sort(key=lambda v: (
        -(v>>20) if x_reverse else v>>20,
        -(Y[v&((1<<20)-1)]>>20) if y_reverse else Y[v&((1<<20)-1)]>>20,
    ))
    
    for i in range(1,n):
        a,b = X[i-1],X[i]
        assert (a>>20, Y[a&((1<<20)-1)]>>20) != (b>>20, Y[b&((1<<20)-1)]>>20), "同一点の重複は不可"
    g = [[] for _ in range(n)]
    solveDC(0,n)
    return g
