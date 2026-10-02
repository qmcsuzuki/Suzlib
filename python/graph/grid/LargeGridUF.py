# competitive-verifier: TITLE 大規模グリッド用UnionFind

from python.data_structure.unionfind.UnionFind import UnionFind

def LargeGridUF(H,W,blocks):
    """障害物で分割された各行の空き区間を併合し、UnionFind と区間位置表を返す。
    接続は 4 近傍。戻り値は (UF, blockpos)。

    blocks は盤面内の障害物座標列。H + len(blocks) < 2^20 を仮定する。
    blockpos[i] の各値は 区間開始列 * 2^20 + UF の要素番号。
    UF には未使用の要素もあるため、全 leader 数は空き領域数と一致するとは限らない。
    K = H + len(blocks) として時間 O(K log K)、空間 O(K)。
    """
    UF = UnionFind(H+len(blocks))
    M = 1<<20
    MM = M*2
    # events: (j,flag,i) の 1 次元化
    # j 列目において、i行目で区間が終了(flag=0) or 開始(flag=1)
    # 区間は半開区間
    events = []
    # 各行を区間に変換    
    blockpos = [[-1] for _ in range(H)]
    for i,j in blocks:
        blockpos[i].append(j)
    for i,lst in enumerate(blockpos):
        lst.sort()
        lst.append(W)
        for j in range(len(lst)-1):
            if lst[j]+1 < lst[j+1]:
                events.append((lst[j]+1)*MM+M+i)
                events.append((lst[j+1])*MM+i)

    events.sort()
    blockid = [-1]*H
    blockpos = [[] for _ in range(H)] # (ブロックの開始列番号, UF の id) の一次元化ける
    idx = 0
    for v in events:
        jflag,i = divmod(v,M)
        j, flag = divmod(jflag,2)
        if flag == 0: # 区間終了（ソートしたので、終了が先に処理される）
            blockid[i] = -1
        else: # 区間開始、新しいブロックを作り、上下のブロックと連結させる
            blockid[i] = idx
            blockpos[i].append(j*M + idx)
            if i and blockid[i-1] != -1:
                UF.merge(idx,blockid[i-1])
            if i+1 < H and blockid[i+1] != -1:
                UF.merge(idx,blockid[i+1])
            idx += 1
    return UF, blockpos

from bisect import bisect_left
def get_blockid(i,j):
    """大域変数 blockpos を使い、空きマス (i,j) の区間番号を返す。
    区間番号は UF の要素番号に対応する。計算量 O(log K)。
    呼び出し側で UF, blockpos = LargeGridUF(...) と設定する。障害物には呼ばない。
    """
    M = 1<<20
    lst = blockpos[i]
    idx = bisect_left(lst,(j+1)*M) - 1
    return lst[idx]%M

# https://atcoder.jp/contests/abc413/submissions/67450182
