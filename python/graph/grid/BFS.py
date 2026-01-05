# competitive-verifier: TITLE 格子上の幅優先探索 (Grid BFS)

"""
グリッド上の BFS
- start_list: 始点のリスト（複数始点対応）

return:
- dist: 距離配列
- nxt: 始点に近づく方向（復元用）
"""

from collections import deque
def BFS_grid(board, H, W, start_list):
    dist = [[-1]*W for _ in range(H)]
    nxt = [[-1]*W for _ in range(H)] # nxt の方向は dx,dy の方向 0,1,2,3 で記述
    q = deque()
    
    dx = [1,0,-1,0]
    dy = [0,-1,0,1]
    
    """ initialize """
    for sx,sy in start_list:
        q.append((sx,sy))
        dist[sx][sy] = 0

    while q:
        x,y = q.popleft()
        for i in range(4):
            nx = x + dx[i]
            ny = y + dy[i]
            if nx < 0 or nx >= H or ny < 0 or ny >= W:
                continue
            if board[nx][ny] == "#": #注: 壁は "#" で、他の記号は通過可能と仮定
                continue
            if dist[nx][ny] == -1:
                q.append((nx,ny))
                dist[nx][ny] = dist[x][y] + 1
                nxt[nx][ny] = i^2
    
    return dist, nxt

# https://atcoder.jp/contests/abc405/submissions/66079020
