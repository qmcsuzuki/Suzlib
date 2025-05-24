"""
Cartesian tree を構築。最小値で列を分割する
par[i]: 頂点 i の親を返す(根の親は -1)
order: 葉を先に見るトポロジカル順序（Cartesian tree の帰りがけ順）

注意：「stack 操作１回ですべてを済ませる実装パターンは下部を見よ！！！！」
"""

def Cartesian_tree(A):
    n = len(A)
    par = [-1]*n
    order = []
    for i,ai in enumerate(A):
        cur = i-1
        pre = -1
        while cur != -1 and A[cur] > ai:
            order.append(cur)
            cur, pre = par[cur], cur
        par[i] = cur
        if pre != -1:
            par[pre] = i
    cur = n-1
    while cur != -1:
        order.append(cur)
        cur = par[cur]
    return par, order

"""
Cartesian tree の根および左右の子の配列を返す
"""
def find_root_and_children(par):
    n = len(par)
    left_child = [-1]*n
    right_child = [-1]*n
    for v,p in enumerate(par):
        if p != -1:
            if v < p:
                left_child[p] = v
            else:
                right_child[p] = v
        else:
            root = v
    return root, left_child, right_child

"""
Cartesian tree の左右の子の配列を利用して再帰呼び出しを模倣する
"""
def solve(L,R,idx):
    calc(L,R,idx)
    lc = left_child[idx]
    rc = right_child[idx]
    if lc != -1:
        solve(L,root,lc)
    if rc != -1:
        solve(root+1,R,rc)



"""
Cartesian tree でありがちな計算を stack １回でこなす。
つまり「半開区間A[L:R] の argmin i と、その親 p」を列挙できる
全区間に対応する親は len(A) と設定（-1 でないことに注意）

banhei = 再帰の初期値 = 「min(A)より真に小さい値」
両方の条件が満たされないときは注意
"""
def Cartesian_tree(A,banhei):
    val = [banhei-1]
    pos = [-1]
    A.append(banhei)
    for R,aR in enumerate(A):
        while val[-1] > aR:
            ai = val.pop()
            i = pos.pop()
            L = pos[-1] + 1
            p = L-1 if val[-1] > A[R] else R
            """
            # ai が最小値となる半開区間 A[L:R] が確定
            # i の親 p も確定 （両隣 a[L-1] =val[-1], a[R] = aR のうち大きいほう）
            # 注意：p == -1 のとき、問題や banhei の値によっては場合分けが必要
            """
            #　calc(i,L,R,p)
        val.append(aR)
        pos.append(R)
    if A[-1] == banhei: A.pop()



############################################################
# https://atcoder.jp/contests/abc116/submissions/22690006
############################################################
# n = int(input())
# *h, = map(int,input().split())

# par,order = Cartesian_tree(h)
# ans = 0
# for v in order:
#     ans += h[v] - (h[par[v]] if par[v] != -1 else 0)
# print(ans)
###################################################################
# https://judge.yosupo.jp/submission/47977
###################################################################
