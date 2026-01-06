"""
遅延セグメント木（区間演算、区間更新）
data[] の要素に モノイド X をもつ
lazy[] の要素に Aut(X) をもつ（ただし作用素は「左」から作用とする）
アクセスは0-indexed, 内部のツリーは 1-indexed（つまりすべての和は tree[1]）
関数は半開区間
引数：
    op_X: モノイド演算 (max, min, __add__,ラムダ式,関数定義など)
    e_X: 単位元
    compose: 作用素を合成させる関数[注：普通の関数合成と同じく、左作用](max, min, __add__,ラムダ式,関数定義など)
    mapping(f,x) = f(x) 関数適用
    id_M: 恒等作用素
    N: 処理する区間の長さ
    array: この配列で初期化
"""
""" 作用素の例：
f \mapsto min(f,-)
    compose = min
    funcval = min
    ID_M = INF = 10**18
f \mapsto max(f,-)
    compose = max
    funcval = max
    ID_M = 0
f \mapsto f (定数関数)（区間代入、最後の操作のみが影響する）
compose = lambda f,g: (g if f is ID_M else f)
funcval = lambda f,x: (x if f is ID_M else f)
ID_M = None #Noneではなく、範囲外の数にすると速くなる
"""

class LazySegmentTree:
    #seg = LazySegmentTree(op_X, e_X, mapping, composision_of_Aut_X, id_of_Aut_X, N, array=None):
    def __init__(self, op_X, e_X, mapping, composision_of_Aut_X, id_of_Aut_X, N, array=None):
        #  それぞれ  Xの演算, 単位元, f(x), f\circ g,             Xの恒等変換
        # M が X に作用する
        #__slots__ = ["op_X",  "e_X",  "mapping","compose","id_M","N","log","N0","data","lazy"]
        self.e_X = e_X; self.op_X = op_X; self.mapping = mapping; self.compose = composision_of_Aut_X; self.id_M = id_of_Aut_X
        self.N = N
        self.log = (N-1).bit_length()
        self.N0 = 1<<self.log
        self.data = [e_X]*(2*self.N0)
        self.lazy = [self.id_M]*self.N0
        if array is not None:
            assert N == len(array)
            self.data[self.N0:self.N0+self.N] = array
            for i in range(self.N0-1,0,-1): self.update(i)

    # デバッグ用出力
    def __str__(self):
        s = self._visualize_binarytree(self.lazy, self.e_X).split("\n")
        t = self._visualize_binarytree(self.data, self.e_X).split("\n")
        return "\n".join(s + t)

    # 1点更新
    def point_set(self, p, x):
        p += self.N0
        for i in range(self.log, 0,-1):
            self.push(p>>i)
        self.data[p] = x
        for i in range(1, self.log + 1):
            self.update(p>>i)
 
    # 1点取得
    def point_get(self, p):
        p += self.N0
        for i in range(self.log, 0, -1):
            self.push(p>>i)
        return self.data[p]
 
    # 半開区間[L,R)をopでまとめる
    def prod(self, l, r):
        if l == r: return self.e_X
        l += self.N0
        r += self.N0
        for i in range(self.log, 0, -1):
            if (l>>i)<<i != l:
                self.push(l>>i)
            if (r>>i)<<i != r:
                self.push(r>>i)

        sml = smr = self.e_X
        while l < r:
            if l & 1: 
                sml = self.op_X(sml, self.data[l])
                l += 1
            if r & 1:
                r -= 1
                smr = self.op_X(self.data[r], smr)
            l >>= 1
            r >>= 1
        return self.op_X(sml, smr)
 
    # 全体をopでまとめる
    def all_prod(self): return self.data[1]
 
    # 1点作用
    def apply_point(self, p, f):
        p += self.N0
        for i in range(self.log, 0, -1):
            self.push(p>>i)
        self.data[p] = self.mapping(f, self.data[p])
        for i in range(1, self.log + 1):
            self.update(p>>i)
 
    # 区間作用
    def apply(self, l, r, f):
        if l == r: return
        l += self.N0
        r += self.N0
        for i in range(self.log, 0, -1):
            if (l>>i)<<i != l:
                self.push(l>>i)
            if (r>>i)<<i != r:
                self.push((r-1)>>i)

        l2, r2 = l, r
        while l < r:
            if l & 1: 
                self.all_apply(l, f)
                l += 1
            if r & 1:
                r -= 1
                self.all_apply(r, f)
            l >>= 1
            r >>= 1

        l, r = l2, r2
        for i in range(1, self.log + 1):
            if (l>>i)<<i != l:
                self.update(l>>i)
            if (r>>i)<<i != r:
                self.update((r-1)>>i)
     
    """
    始点 l を固定
    f(x_l*...*x_{r-1}) が True になる最大の r 
    つまり TTTTFFFF となるとき、F となる最小の添え字
    存在しない場合 n が返る
    f(e_M) = True でないと壊れる
    """
    def max_right(self, l, g):
        if l == self.N: return self.N
        l += self.N0
        for i in range(self.log, 0, -1): self.push(l>>i)
        sm = self.e_X
        while True:
            while l&1 == 0:
                l >>= 1
            if not g(self.op_X(sm, self.data[l])):
                while l < self.N0:
                    self.push(l)
                    l *= 2
                    if g(self.op_X(sm, self.data[l])):
                        sm = self.op_X(sm, self.data[l])
                        l += 1
                return l - self.N0
            sm = self.op_X(sm, self.data[l])
            l += 1
            if l&-l == l: break
        return self.N
 
    """
    終点 r を固定
    f(x_l*...*x_{r-1}) が True になる最小の l
    つまり FFFFTTTT となるとき、T となる最小の添え字
    存在しない場合 r が返る
    f(e_M) = True でないと壊れる
    """
    def min_left(self, r, g):
        if r == 0: return 0
        r += self.N0
        for i in range(self.log, 0, -1): self.push((r-1)>>i)
        sm = self.e_X
        while True:
            r -= 1
            while r>1 and r&1:
                r >>= 1
            if not g(self.op_X(self.data[r], sm)):
                while r < self.N0:
                    self.push(r)
                    r = 2*r + 1
                    if g(self.op_X(self.data[r], sm)):
                        sm = self.op_X(self.data[r], sm)
                        r -= 1
                return r + 1 - self.N0
            sm = self.op_X(self.data[r], sm)
            if r&-r == r: break
        return 0
        
    # 以下内部関数
    def update(self, k):
        self.data[k] = self.op_X(self.data[2*k], self.data[2*k+1])
    
    def all_apply(self, k, f):
        self.data[k] = self.mapping(f, self.data[k])
        if k < self.N0:
            self.lazy[k] = self.compose(f, self.lazy[k])

    def push(self, k): #propagate と同じ
        if self.lazy[k] is self.id_M: return
        self.data[2*k  ] = self.mapping(self.lazy[k], self.data[2*k])
        self.data[2*k+1] = self.mapping(self.lazy[k], self.data[2*k+1])
        if 2*k < self.N0:
            self.lazy[2*k]   = self.compose(self.lazy[k], self.lazy[2*k])
            self.lazy[2*k+1] = self.compose(self.lazy[k], self.lazy[2*k+1])
        self.lazy[k] = self.id_M

    def _visualize_binarytree(self, A, v=1<<60):
        h = len(A).bit_length() - 1 # height of tree
        assert len(A) == 1<<h
        S = ["INF" if isinstance(v,int) and isinstance(x,int) and x >= v else str(x) for x in A] # large value is displayed "INF"
        layers = [S[1<<i:2<<i] for i in range(h)] # layer of tree
        W = max(2+(max(map(len,lst)))<<i for i,lst in enumerate(layers)) # width of displayed tree
        return "".join("".join(f"{T:^{W>>i}}" for T in lst) + "\n" for i,lst in enumerate(layers))
