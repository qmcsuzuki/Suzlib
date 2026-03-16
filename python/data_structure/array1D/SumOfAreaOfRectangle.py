class UnionOfLines:
    """
    区間の追加 / 削除を行い、被覆長を管理するデータ構造。

    想定用途:
        座標圧縮した 1 次元区間の和集合長を管理する。
        width[i] は葉 i に対応する基本区間の物理的な長さ。

    内部の不変条件:
        - lazy[k]: ノード k の区間全体を「丸ごと」覆っている本数
        - data[k]:「lazy[k] == 0 だと仮定したとき」の、その部分木内の未被覆長
        - よって、ノード k の実際の未被覆長は
              0        (lazy[k] > 0 のとき)
              data[k]  (lazy[k] == 0 のとき)
    """

    def __init__(self, N, width=None):
        self.N = N
        self.data = [0] * (2 * N)
        self.lazy = [0] * (2 * N)
        if width is None:
            width = [1] * N
        self.total = sum(width)
        assert N == len(width)
        self.data[self.N : 2 * self.N] = width
        for k in range(self.N - 1, 0, -1):
            self.data[k] = self.data[2 * k] + self.data[2 * k + 1]

    def _update_above(self, k):
        while k >= 2:
            k >>= 1
            self.data[k] = (0 if self.lazy[2 * k] else self.data[2 * k]) \
                         + (0 if self.lazy[2 * k + 1] else self.data[2 * k + 1])

    # 座標 p が覆われているか
    def is_covered(self, p):
        p += self.N
        while p >= 1:
            if self.lazy[p]:
                return True
            p >>= 1
        return False

    # 区間の union の合計長
    def all_prod(self):
        return self.total - (0 if self.lazy[1] else self.data[1])

    # 半開区間 [l,r) に f を足す
    def apply(self, l, r, f):
        if l == r:
            return
        l += self.N
        r += self.N
        L, R = l // (l & -l), r // (r & -r)
        while l < r:
            if l & 1:
                self.lazy[l] += f
                l += 1
            if r & 1:
                r -= 1
                self.lazy[r] += f
            l >>= 1
            r >>= 1
        self._update_above(L)
        self._update_above(R - 1)


class AreaOfUnionOfRectangles:
    MMM = 1 << 31

    def sorted_tuples(self, lists, key):
        idx = sorted(key(lst) * self.MMM + i for i, lst in enumerate(lists))
        return [lists[i % self.MMM] for i in idx]

    def __init__(self):
        self.queries = []
        self.y_coord = []

    # [l,r) * [d,u) を追加
    def add_query(self, l, d, r, u):
        self.y_coord.append(d)
        self.y_coord.append(u)
        val = 2 * (self.MMM * d + u)
        self.queries.append((l, val + 1))  # add segment
        self.queries.append((r, val + 0))  # remove segment

    def solve_with_zaatu(self):
        from random import getrandbits

        if not self.queries:
            return 0

        RANDOM = getrandbits(20)

        self.y_coord.sort()
        ys = [self.y_coord[0]]
        for y in self.y_coord[1:]:
            if ys[-1] != y:
                ys.append(y)
        if len(ys) <= 1:
            return 0
        zaatu_y = {v ^ RANDOM: i for i, v in enumerate(ys)}

        ans = y_width = 0
        events = self.sorted_tuples(self.queries, key=lambda lst: lst[0])
        prev = events[0][0]
        seg = UnionOfLines(len(ys) - 1, [j - i for i, j in zip(ys, ys[1:])])

        for x, duv in events:
            ans += y_width * (x - prev)
            d, u = divmod(duv >> 1, self.MMM)
            seg.apply(zaatu_y[d ^ RANDOM], zaatu_y[u ^ RANDOM], 2 * (duv & 1) - 1)
            y_width = seg.all_prod()
            prev = x
        return ans

    def solve_without_zaatu(self, y_max):
        assert y_max < 1 << 20

        ans = y_width = prev = 0
        seg = UnionOfLines(y_max + 1)
        for x, duv in self.sorted_tuples(self.queries, key=lambda lst: lst[0]):
            ans += y_width * (x - prev)
            d, u = divmod(duv >> 1, self.MMM)
            seg.apply(d, u, 2 * (duv & 1) - 1)
            y_width = seg.all_prod()
            prev = x

        return ans
