# competitive-verifier: TITLE 斜め2次元累積和

from python.data_structure_2D.Accumulate2dim import Accumulate2dim


def _ceil_div2(x):
    return (x + 1) // 2


class DiagonalAccumulate2dim:
    """
    a: h*w 行列

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
        self.u_base = [0, 0]
        self.v_base = [0, 0]

        # x+y と x-y は同じ parity を持つので、偶奇ごとに圧縮する。
        for r in range(2):
            ub = _ceil_div2(self.u_min - r)
            ue = _ceil_div2(self.u_max - r)
            vb = _ceil_div2(self.v_min - r)
            ve = _ceil_div2(self.v_max - r)
            self.u_base[r] = ub
            self.v_base[r] = vb
            if ub == ue or vb == ve:
                continue

            b = [[0] * (ve - vb) for _ in range(ue - ub)]
            for x in range(self.h):
                for y in range(self.w):
                    u = x + y
                    if (u & 1) != r:
                        continue
                    v = x - y
                    b[(u - r) // 2 - ub][(v - r) // 2 - vb] = a[x][y]
            self.acc[r] = Accumulate2dim(b)

    def range_sum(self, a, b, c, d):
        """a <= x+y < b, c <= x-y < d を満たす要素の和を返す。"""
        assert a <= b and c <= d
        ans = 0
        for r in range(2):
            acc = self.acc[r]
            if acc is None:
                continue

            u1 = _ceil_div2(a - r) - self.u_base[r]
            u2 = _ceil_div2(b - r) - self.u_base[r]
            v1 = _ceil_div2(c - r) - self.v_base[r]
            v2 = _ceil_div2(d - r) - self.v_base[r]

            u1 = max(0, min(acc.h, u1))
            u2 = max(0, min(acc.h, u2))
            v1 = max(0, min(acc.w, v1))
            v2 = max(0, min(acc.w, v2))
            if u1 < u2 and v1 < v2:
                ans += acc.range_sum(u1, u2, v1, v2)
        return ans

    def up(self, x, y):
        """(x,y) から見て上側 y'-y >= |x'-x| の要素和を返す。境界を含む。"""
        return self.range_sum(x + y, self.u_max, self.v_min, x - y + 1)

    def right(self, x, y):
        """(x,y) から見て右側 x'-x >= |y'-y| の要素和を返す。境界を含む。"""
        return self.range_sum(x + y, self.u_max, x - y, self.v_max)

    def down(self, x, y):
        """(x,y) から見て下側 y-y' >= |x'-x| の要素和を返す。境界を含む。"""
        return self.range_sum(self.u_min, x + y + 1, x - y, self.v_max)

    def left(self, x, y):
        """(x,y) から見て左側 x-x' >= |y'-y| の要素和を返す。境界を含む。"""
        return self.range_sum(self.u_min, x + y + 1, self.v_min, x - y + 1)
