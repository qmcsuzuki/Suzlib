# competitive-verifier: TITLE 次出現位置テーブル
"""
s を 1-indexed で見る
nxt[i][j] = i+1 文字目以降に文字種 j の最初のindex
"""
def next_index(s):
    N = len(s)
    D = [-1]*26
    nxt = [None]*(N+1)
    a = ord('a')
    for i in range(1,N+1)[::-1]:
        nxt[i] = D[:]
        D[ord(s[i-1])-a] = i
    nxt[0] = D
    return nxt
