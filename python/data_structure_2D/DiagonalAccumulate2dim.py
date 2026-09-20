# competitive-verifier: TITLE 斜め2次元累積和


class DiagonalAccumulate2dim:
    """
    a: h*w 行列

    x は下向き、y は右向きとする行列座標を用いる。
    u = x+y, v = x-y として、斜め方向の静的 range sum を扱う。
    range_sum(a,b,c,d) は
        a <= x+y < b, c <= x-y < d
    を満たす要素の和を返す。
    """
    def __init__(self, a):
        self.h = len(a)
        self.w = len(a[0])
        self.u_min = 0
        self.u_max = self.h + self.w - 1
        self.v_min = 1 - self.w
        self.v_max = self.h

        self.acc = [None, None]
        self.shape = [None, None]
        self.u_base = [0, 0]
        self.v_base = [0, 0]

        # x+y と x-y は同じ parity を持つので、偶奇ごとに圧縮する。
        for r in range(2):
            ub = (self.u_min - r + 1) // 2
            ue = (self.u_max - r + 1) // 2
            vb = (self.v_min - r + 1) // 2
            ve = (self.v_max - r + 1) // 2
            self.u_base[r] = ub
            self.v_base[r] = vb
            h = ue - ub
            w = ve - vb
            self.shape[r] = (h, w)
            if h and w:
                self.acc[r] = [0] * ((h + 1) * (w + 1))

        # 変換後の位置へ直接書き込む。
        for x in range(self.h):
            for y in range(self.w):
                u = x + y
                v = x - y
                r = u & 1
                h, w = self.shape[r]
                stride = w + 1
                i = (u - r) // 2 - self.u_base[r] + 1
                j = (v - r) // 2 - self.v_base[r] + 1
                self.acc[r][i * stride + j] = a[x][y]

        # 各 parity について in-place で2次元累積和を構築する。
        for r in range(2):
            acc = self.acc[r]
            if acc is None:
                continue
            h, w = self.shape[r]
            stride = w + 1
            for i in range(1, h + 1):
                row = i * stride
                prev = row - stride
                s = 0
                for j in range(1, w + 1):
                    s += acc[row + j]
                    acc[row + j] = s + acc[prev + j]

    def range_sum(self, a, b, c, d):
        """a <= x+y < b, c <= x-y < d を満たす要素の和を返す。"""
        assert a <= b and c <= d
        ans = 0
        for r in range(2):
            acc = self.acc[r]
            if acc is None:
                continue
            h, w = self.shape[r]

            u1 = (a - r + 1) // 2 - self.u_base[r]
            u2 = (b - r + 1) // 2 - self.u_base[r]
            v1 = (c - r + 1) // 2 - self.v_base[r]
            v2 = (d - r + 1) // 2 - self.v_base[r]

            u1 = max(0, min(h, u1))
            u2 = max(0, min(h, u2))
            v1 = max(0, min(w, v1))
            v2 = max(0, min(w, v2))
            if u1 < u2 and v1 < v2:
                stride = w + 1
                ans += (acc[u2 * stride + v2]
                        - acc[u1 * stride + v2]
                        - acc[u2 * stride + v1]
                        + acc[u1 * stride + v1])
        return ans

    def up(self, x, y):
        """(x,y) から見て上側 x-x' >= |y'-y| の要素和を返す。境界を含む。"""
        return self.range_sum(self.u_min, x + y + 1, self.v_min, x - y + 1)

    def right(self, x, y):
        """(x,y) から見て右側 y'-y >= |x'-x| の要素和を返す。境界を含む。"""
        return self.range_sum(x + y, self.u_max, self.v_min, x - y + 1)

    def down(self, x, y):
        """(x,y) から見て下側 x'-x >= |y'-y| の要素和を返す。境界を含む。"""
        return self.range_sum(x + y, self.u_max, x - y, self.v_max)

    def left(self, x, y):
        """(x,y) から見て左側 y-y' >= |x'-x| の要素和を返す。境界を含む。"""
        return self.range_sum(self.u_min, x + y + 1, x - y, self.v_max)
