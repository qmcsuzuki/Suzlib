# competitive-verifier: TITLE グリッドを相対座標で持って移動するユーティリティ

class GridPath:
    """
    0-indexed の局所盤面ビュー + 経路履歴。
    局所座標 (i, j) の絶対座標は
        abs_pos(i, j) = O + i * D + j * R

    move 系:
        実際に移動し、絶対座標を履歴に追加する。

    view 系:
        局所盤面の見方を変える
        現在位置や target は新しい局所座標へ自動で変換する。
    """

    def __init__(self, h, w, start=(0, 0), target=(0, 0)):
        self.h = h
        self.w = w

        self.ox = 0; self.oy = 0 # 原点の絶対座標
        self.dx = 1; self.dy = 0 # 相対座標での下移動が表す絶対移動ベクトル
        self.rx = 0; self.ry = 1 # 相対座標での右移動が表す絶対移動ベクトル
        self.target_i, self.target_j = target

        self.cx, self.cy = start # 現在位置
        self.history = [(self.cx, self.cy)] # 移動したマスの履歴

    def abs_pos(self, i, j): # 絶対位置
        return (
            self.ox + i * self.dx + j * self.rx,
            self.oy + i * self.dy + j * self.ry,
        )

    def relative_current_pos(self): # （相対の）現在位置
        return self.cx, self.cy

    def relative_target(self):
        return self.target_i, self.target_j

    def move_to(self, i, j):
        """
        現在の局所盤面で (i,j) へ 1 手で移動し、履歴に追加する。
        """
        self.cx = i
        self.cy = j
        self.history.append(self.abs_pos(i, j))

    def move(self, di, dj):
        self.move_to(self.cx + di, self.cy + dj)

    def up(self): self.move(-1, 0)
    def down(self): self.move(1, 0)
    def left(self): self.move(0, -1)
    def right(self): self.move(0, 1)

    def upleft(self): self.move(-1, -1)
    def upright(self): self.move(-1, 1)
    def downleft(self): self.move(1, -1)
    def downright(self): self.move(1, 1)

    def _map_local_points(self, f):
        self.cx, self.cy = f(self.cx, self.cy)
        self.target_i, self.target_j = f(self.target_i, self.target_j)

    def flip_ud(self):
        """
        上下反転: new(i,j) = old(h - 1 - i, j)
        """
        h = self.h

        self.ox += (h - 1) * self.dx
        self.oy += (h - 1) * self.dy

        self.dx = -self.dx
        self.dy = -self.dy

        self._map_local_points(lambda i, j: (h - 1 - i, j))

    def flip_lr(self):
        """
        左右反転: new(i,j) = old(i, w - 1 - j)
        """
        w = self.w

        self.ox += (w - 1) * self.rx
        self.oy += (w - 1) * self.ry

        self.rx = -self.rx
        self.ry = -self.ry

        self._map_local_points(lambda i, j: (i, w - 1 - j))

    def transpose(self):
        """
        転置: new(i,j) = old(j,i)
        """
        self.h, self.w = self.w, self.h
        self.dx, self.rx = self.rx, self.dx
        self.dy, self.ry = self.ry, self.dy

        self._map_local_points(lambda i, j: (j, i))

    def cut_left(self):
        """
        左端列を実際に通ってから、残り盤面へ遷移する。
        現在位置は相対座標で (0,0) 始まり、(0,0) 終わり

        操作: 下にぶつかるまで移動, 右に 1 回移動, 座標系を張り替える
        """
        assert self.cx == 0 and self.cy == 0

        for _ in range(self.h - 1):
            self.down()
        self.right()

        self.ox += (self.h - 1) * self.dx + self.rx
        self.oy += (self.h - 1) * self.dy + self.ry

        self.dx = -self.dx
        self.dy = -self.dy

        self.w -= 1

        self._map_local_points(lambda i, j: (self.h - 1 - i, j - 1))

    def cut_top(self):
        """
        左端列を実際に通ってから、残り盤面へ遷移する。
        現在位置は相対座標で (0,0) 始まり、(0,0) 終わり

        操作: 右にぶつかるまで移動, 下に 1 回移動, 座標系を張り替える
        """
        assert self.cx == 0 and self.cy == 0

        for _ in range(self.w - 1):
            self.right()
        self.down()

        self.ox += self.dx + (self.w - 1) * self.rx
        self.oy += self.dy + (self.w - 1) * self.ry

        self.rx = -self.rx
        self.ry = -self.ry

        self.h -= 1

        self._map_local_points(lambda i, j: (i - 1, self.w - 1 - j))

    def history_UDLR(self):
        """
        history から移動列を "UDLR" 文字列として返す。
        斜め移動が含まれる場合は ValueError。
        """
        res = []
    
        for (x1, y1), (x2, y2) in zip(self.history, self.history[1:]):
            dx = x2 - x1
            dy = y2 - y1
    
            if dx == -1 and dy == 0:
                res.append("U")
            elif dx == 1 and dy == 0:
                res.append("D")
            elif dx == 0 and dy == -1:
                res.append("L")
            elif dx == 0 and dy == 1:
                res.append("R")
            else:
                raise ValueError(f"not a UDLR move: ({x1}, {y1}) -> ({x2}, {y2})")
    
        return "".join(res)
