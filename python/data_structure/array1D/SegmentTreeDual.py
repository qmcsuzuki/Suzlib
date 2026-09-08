# competitive-verifier: TITLE Segment Tree Dual（区間更新・一点取得）

"""
双対セグメント木
- apply(l,r,f): 区間に（左から）f を乗算
- apply_to_point(i,x): モノイド作用を値 x に行う
- point_get(i): 1点取得
- all_get(): 全点取得
- point_set(i): 1点の値を変更
"""
#SegmentTreeDual(N, op, e, is_commutative=False, init=None, mapping=None)
class SegmentTreeDual:
    """区間への作用と一点取得を管理する双対セグメント木。"""
    def __init__(self, N, op, e, is_commutative=False, init=None, mapping=None):
        """作用の合成と単位元を設定し、N 要素の双対セグメント木を構築する。"""
        self.N = N
        self.op = op
        self.id_M = e
        self.mapping = mapping

        self.height = (N-1).bit_length() #木の段数
        self.lazy = [e]*(2*N)
        if is_commutative:
            self.apply = self.apply_commutative
        
        if init is not None:
            self.lazy[N:2*N] = list(init)
    
    # 半開区間[l,r) 上に f を左から乗算
    def apply(self,L,R,f):
        """半開区間 [L,R) に作用 f を、適用順を保って合成する。"""
        L += self.N; R += self.N
        self.thrust(L)
        self.thrust(R-1)
        while L < R:
            if R & 1:
                self.lazy[R-1] = self.op(f, self.lazy[R-1])
            if L & 1:
                self.lazy[L] = self.op(f, self.lazy[L])
            L = (L+1)>>1; R >>= 1

    # 半開区間[l,r) 上に f を左から乗算（モノイドが可換なときは伝搬がいらない）
    def apply_commutative(self,L,R,f):
        """作用の可換性を仮定して半開区間 [L,R) に f を合成する。"""
        L += self.N; R += self.N
        while L < R:
            if R & 1:
                self.lazy[R-1] = self.op(f, self.lazy[R-1])
            if L & 1:
                self.lazy[L] = self.op(f, self.lazy[L])
            L = (L+1)>>1; R >>= 1
    
    # values[k] を取得
    def point_get(self, k):
        """指定した位置の値を返す。"""
        res = self.lazy[k+self.N]
        k = (k+self.N)>>1
        while k:
            res = self.op(self.lazy[k], res)
            k >>= 1
        return res

    # values[k](x) を取得
    def apply_to_point(self, k, x):
        """指定位置に蓄積した作用を値 x に適用した結果を返す。"""
        k += self.N
        while k:
            x = self.mapping(self.lazy[k], x)
            k >>= 1
        return x
    
    def all_get(self):
        """遅延された更新を反映した全要素をリストで返す。"""
        self.all_propagate()
        return self.lazy[self.N:self.N*2]
        
    # values[k] = x 代入する
    def point_set(self, k, x): 
        """指定した位置の値を上書きする。"""
        self.thrust(k+self.N)
        self.lazy[k+self.N] = x

    def __str__(self):
        """現在の内容を表示用文字列に変換する。"""
        v = 2**(len(self.lazy)-1).bit_length() - len(self.lazy)
        return self._visualize_binarytree(self.lazy+["x"]*(v), self.op, self.id_M)
        
    # 補助関数---------------------------------------------
    # lazy[k] の情報を子に伝搬
    def _visualize_binarytree(self,A,op,v):
        """内部配列を二分木の層ごとに整形した文字列を返す。"""
        h = len(A).bit_length() - 1 # height of tree
        assert len(A) == 1<<h
        is_min = (op == min and isinstance(v,int))
        S = ["INF" if is_min and isinstance(x,int) and x >= v else str(x) for x in A] # large value is displayed "INF"
        layers = [S[1<<i:2<<i] for i in range(h)] # layer of tree
        W = max(2+(max(map(len,lst)))<<i for i,lst in enumerate(layers)) # width of displayed tree
        return "".join("".join(f"{T:^{W>>i}}" for T in lst) + "\n" for i,lst in enumerate(layers))

    def propagate(self,k):
        """指定ノードの遅延作用を左右の子へ伝播する。"""
        if self.lazy[k] == self.id_M: return;
        if k < self.N:
            self.lazy[2*k  ] = self.op(self.lazy[k], self.lazy[2*k  ])
            self.lazy[2*k+1] = self.op(self.lazy[k], self.lazy[2*k+1])
            self.lazy[k] = self.id_M
    
    # 遅延をすべて解消する
    def all_propagate(self):
        """すべての遅延作用を葉まで伝播する。"""
        for i in range(1,self.N): self.propagate(i)

    # laz[k]およびその上に位置する作用素をすべて伝播
    def thrust(self,k):
        """指定ノードの祖先にある遅延作用を根から順に伝播する。"""
        v = self.height if k>>self.height != 0 else self.height-1
        for i in range(v,-1,-1):
            self.propagate(k>>i)
