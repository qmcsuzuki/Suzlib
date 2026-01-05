# competitive-verifier: TITLE 大規模グリッド用UnionFind

def LargeGridUF(H,W,blocks):
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
    M = 1<<20
    lst = blockpos[i]
    idx = bisect_left(lst,(j+1)*M) - 1
    return lst[idx]%M

# https://atcoder.jp/contests/abc413/submissions/67450182
