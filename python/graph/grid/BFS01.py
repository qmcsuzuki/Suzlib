# verification-helper: TITLE 01 BFS

from collections import deque
def BFS01(board,start_list):
    H,W = len(board), len(board[0])
    INF = 1<<60
    dist = [[INF]*W for _ in range(H)]
    dx = [1,0,-1,0]
    dy = [0,-1,0,1]
    
    q = deque()
    for sx,sy in start_list:
        q.append((sx,sy,0))
        dist[sx][sy] = 0

    while q:
        x,y,d = q.popleft()
        for i in range(4):
            nx = x + dx[i]
            ny = y + dy[i]
            if nx < 0 or nx >= H or ny < 0 or ny >= W:
                continue

            if board[nx][ny] == "X": #注: 壁は "X" で、他の記号は通過可能と仮定
                continue

            if board[nx][ny] == 0: # 注: 「壊せる壁」を"#" と仮定"
                if dist[nx][ny] > d+1:
                    dist[nx][ny] = d+1
                    q.append((nx,ny,d+1))
            else:
                if dist[nx][ny] > d:
                    dist[nx][ny] = d
                    q.appendleft((nx,ny,d))
    
    return dist

# https://atcoder.jp/contests/arc177/submissions/66153761
