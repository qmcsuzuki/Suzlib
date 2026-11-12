# competitive-verifier: TITLE 多値の Min Cut Optimization（燃やす埋める）

from python.graph.flow.maxflow.MinCutOptimization import MinCutOptimization


class MultiLabelMinCutOptimization:
    """変数 i の値域を 0, ..., label_counts[i]-1 としてコストの総和を最小化する。
    単項コストは任意、異なる変数の二項コストには Monge 性を要求する。
    閾値 [x_i >= a] ごとに 1 頂点を使い、solve() で最大流を 1 回解く。

    例:
        g = MultiLabelMinCutOptimization([3, 3])
        g.add_unary(0, [4, 1, 0])
        for a in range(1, 3):
            g.add_if_ge_then_ge(0, a, 1, a)  # x[0] <= x[1]
        cost, x = g.solve()  # (0, [2, 2])
    """

    def __init__(self, label_counts: list[int]) -> None:
        self._start = [0]
        for k in label_counts:
            assert k >= 1
            self._start.append(self._start[-1] + k - 1)
        self._cut = MinCutOptimization(self._start[-1])
        for start, end in zip(self._start, self._start[1:]):
            for u in range(start + 1, end):
                self._cut.add_if1then1(u, u - 1)

    def _count(self, i: int) -> int:
        assert 0 <= i < len(self._start) - 1
        return self._start[i + 1] - self._start[i] + 1

    def _threshold(self, i: int, a: int) -> int:
        assert 1 <= a < self._count(i)
        return self._start[i] + a - 1

    def add_constant(self, cost: int) -> None:
        """定数項を加える。"""
        self._cut.add_constant(cost)

    def add_unary(self, i: int, costs: list[int]) -> None:
        """costs[x_i] を加える。O(k_i)。"""
        assert len(costs) == self._count(i)
        self._cut.add_constant(costs[0])
        for a in range(1, len(costs)):
            self._cut.add_cost_true(self._start[i] + a - 1, costs[a] - costs[a - 1])

    def add_penalty_ge_lt(self, i: int, a: int, j: int, b: int, cost: int) -> None:
        """x_i >= a かつ x_j < b のとき cost >= 0 を加える。1 <= a < k_i, 1 <= b < k_j。"""
        self._cut.add_penalty(self._threshold(i, a), self._threshold(j, b), cost)

    def add_if_ge_then_ge(self, i: int, a: int, j: int, b: int) -> None:
        """x_i >= a なら x_j >= b を強制する。1 <= a < k_i, 1 <= b < k_j。"""
        self._cut.add_if1then1(self._threshold(i, a), self._threshold(j, b))

    def add_pairwise(self, i: int, j: int, costs: list[list[int]]) -> None:
        """costs[x_i][x_j] を加える。i == j では対角成分だけを使う。
        O(k_i k_j) 時間。Monge 不等式が狭義の隣接 2 x 2 小行列ごとに 1 辺を追加する。
        """
        rows, cols = self._count(i), self._count(j)
        assert len(costs) == rows and all(len(row) == cols for row in costs)
        if i == j:
            self.add_unary(i, [row[a] for a, row in enumerate(costs)])
            return

        # 各行の横差分が下の行ほど小さいことが Monge 条件。追加前に検査する。
        for a in range(1, rows):
            prev, curr = costs[a - 1], costs[a]
            assert all(prev[b] - prev[b - 1] >= curr[b] - curr[b - 1]
                       for b in range(1, cols)), "pairwise costs must be Monge"

        # 最終列と先頭行が単項部分。右上隅は二重に数えるので引く。
        self.add_unary(i, [row[-1] for row in costs])
        self.add_unary(j, costs[0])
        self.add_constant(-costs[0][-1])
        for a in range(1, rows):
            prev, curr = costs[a - 1], costs[a]
            u = self._start[i] + a - 1
            for b in range(1, cols):
                weight = prev[b] - prev[b - 1] - curr[b] + curr[b - 1]
                if weight:
                    self._cut.add_penalty(u, self._start[j] + b - 1, weight)

    def solve(self) -> tuple[int, list[int]]:
        """最小コストと元の各変数の最適ラベルを返す。呼び出しは 1 回のみ。"""
        cost, bits = self._cut.solve()
        return cost, [sum(bits[start:end]) for start, end in zip(self._start, self._start[1:])]
