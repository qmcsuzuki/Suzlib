# competitive-verifier: TITLE 多値の Min Cut Optimization（燃やす埋める）

from __future__ import annotations

from typing import Callable, Literal

from python.graph.flow.maxflow.MinCutOptimization import MinCutOptimization


class MultiLabelMinCutOptimization:
    """変数 i の値域を 0, ..., label_counts[i]-1 としてコストの総和を最小化する。
    単項コストは任意、異なる変数の二項コストには Monge 性を要求する。
    閾値 [x_i >= a] ごとに 1 頂点を使い、solve() で最大流を 1 回解く。

    例:
        g = MultiLabelMinCutOptimization([3, 3])
        g.add_unary(0, [4, 1, 0])
        g.add_ge(1, 0)  # x[1] >= x[0]
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
                self._cut.add_implication(u, u - 1, True)

    def _count(self, i: int) -> int:
        assert 0 <= i < len(self._start) - 1
        return self._start[i + 1] - self._start[i] + 1

    def _threshold(self, i: int, a: int) -> int:
        assert 1 <= a < self._count(i)
        return self._start[i] + a - 1

    def add_constant(self, cost: int) -> None:
        """定数項を加える。"""
        self._cut.add_constant(cost)

    def add_unary(self, i: int, costs: list[int | Literal["inf"]]) -> None:
        """costs[x_i] を加える。"inf" はそのラベルを禁止する。O(k_i)。"""
        k = self._count(i)
        assert len(costs) == k
        if all(cost == "inf" for cost in costs):
            raise ValueError("unary costs must have a finite entry")
        prev = 0
        for a, cost in enumerate(costs):
            if cost == "inf":
                # x_i = a を除くため、x_i >= a なら x_i >= a+1 を強制する。
                if a == 0:
                    self._cut.force(self._threshold(i, 1), True)
                elif a == k - 1:
                    self._cut.force(self._threshold(i, a), False)
                else:
                    self.add_if_ge_then_ge(i, a, i, a + 1)
                continue
            if a == 0:
                self.add_constant(cost)
            elif cost != prev:
                self._cut.add_unary_cost(self._threshold(i, a), 0, cost - prev)
            prev = cost

    def add_penalty_ge_lt(self, i: int, a: int, j: int, b: int, cost: int) -> None:
        """x_i >= a かつ x_j < b のとき cost >= 0 を加える。1 <= a < k_i, 1 <= b < k_j。"""
        self._cut.add_penalty(self._threshold(i, a), self._threshold(j, b), cost)

    def add_if_ge_then_ge(self, i: int, a: int, j: int, b: int) -> None:
        """x_i >= a なら x_j >= b を強制する。1 <= a < k_i, 1 <= b < k_j。"""
        self._cut.add_implication(self._threshold(i, a), self._threshold(j, b), True)

    def add_ge(self, i: int, j: int, d: int = 0) -> None:
        """x_i >= x_j + d を強制する。単独で実行不能なら ValueError。O(min(k_i, k_j))。"""
        rows, cols = self._count(i), self._count(j)
        if d >= rows or (i == j and d > 0):
            raise ValueError("infeasible difference bound")
        if i == j:
            return
        if d > 0:
            self._cut.force(self._threshold(i, d), True)
        for a in range(max(1, 1 - d), min(cols, rows - d)):
            self.add_if_ge_then_ge(j, a, i, a + d)
        if rows - d < cols:
            self._cut.force(self._threshold(j, rows - d), False)

    def add_penalty_ge(self, i: int, j: int, d: int, weight: int) -> None:
        """x_i >= x_j + d の違反量 max(0, x_j + d - x_i) に weight >= 0 を掛けて加える。O(k_i + k_j)。"""
        rows, cols = self._count(i), self._count(j)
        assert weight >= 0
        if i == j:
            self.add_constant(max(0, d) * weight)
            return
        if weight == 0 or cols - 1 + d <= 0:
            return
        # x_i < t <= x_j + d となる整数 t を数える。
        for t in range(1, min(rows, d + 1)):
            self._cut.add_unary_cost(self._threshold(i, t), weight, 0)
        for a in range(max(1, 1 - d), min(cols, rows - d)):
            self.add_penalty_ge_lt(j, a, i, a + d, weight)
        # t >= rows では x_i < t が常に成立する。
        self.add_constant(max(0, d - rows + 1) * weight)
        for a in range(max(1, rows - d), cols):
            self._cut.add_unary_cost(self._threshold(j, a), 0, weight)

    def add_abs_diff(self, i: int, j: int, weight: int) -> None:
        """weight * abs(x_i - x_j) を加える。weight >= 0。O(k_i + k_j)。"""
        self.add_penalty_ge(i, j, 0, weight)
        self.add_penalty_ge(j, i, 0, weight)

    def add_convex_diff(self, i: int, j: int, g: Callable[[int], int]) -> None:
        """有限な整数値をとる離散凸関数 g について g(x_i - x_j) を加える。O(k_i k_j)。"""
        rows, cols = self._count(i), self._count(j)
        if i == j:
            cost = g(0)
            assert isinstance(cost, int)
            self.add_constant(cost)
            return
        values = [g(d) for d in range(1 - cols, rows)]
        assert all(isinstance(v, int) for v in values), "g must return integers"
        assert all(values[t - 1] + values[t + 1] >= 2 * values[t]
                   for t in range(1, len(values) - 1)), "g must be convex"
        # 行 a は g(a), g(a-1), ..., g(a-cols+1)。
        self.add_pairwise(i, j, [values[a:a + cols][::-1] for a in range(rows)])

    def add_reward_all_ge(self, conditions: list[tuple[int, int]], reward: int) -> None:
        """(i, a) の条件がすべて x_i >= a なら報酬を与える。1 <= a < k_i。"""
        self._cut.add_reward_all_true([self._threshold(i, a) for i, a in conditions], reward)

    def add_reward_all_lt(self, conditions: list[tuple[int, int]], reward: int) -> None:
        """(i, a) の条件がすべて x_i < a なら報酬を与える。1 <= a < k_i。"""
        self._cut.add_reward_all_false([self._threshold(i, a) for i, a in conditions], reward)

    def add_penalty_any_ge(self, conditions: list[tuple[int, int]], cost: int) -> None:
        """(i, a) の条件がいずれかが x_i >= a ならペナルティを与える。1 <= a < k_i。"""
        self._cut.add_penalty_any_true([self._threshold(i, a) for i, a in conditions], cost)

    def add_penalty_any_lt(self, conditions: list[tuple[int, int]], cost: int) -> None:
        """(i, a) の条件がいずれかが x_i < a ならペナルティを与える。1 <= a < k_i。"""
        self._cut.add_penalty_any_false([self._threshold(i, a) for i, a in conditions], cost)

    def add_pairwise(self, i: int, j: int, costs: list[list[int | Literal["inf"]]]) -> None:
        """costs[x_i][x_j] を加える。i == j では対角成分だけを使う。
        "inf" は右上または左下に広がる階段状の禁止領域に使える。有限成分を 1 個以上必要とする。
        O(k_i k_j) 時間。Monge 不等式が狭義の隣接 2 x 2 小行列ごとに 1 辺を追加する。
        """
        rows, cols = self._count(i), self._count(j)
        assert len(costs) == rows and all(len(row) == cols for row in costs)
        if i == j:
            diagonal = [row[a] for a, row in enumerate(costs)]
            self.add_unary(i, diagonal)
            return

        widths = []
        if any("inf" in row for row in costs):
            # 転置で禁止領域を右上にそろえ、各行の有限な接頭部の長さを求める。
            if costs[0][-1] != "inf":
                costs = list(zip(*costs))
                i, j = j, i
                rows, cols = cols, rows
            costs = [list(row) for row in costs]
            for row in costs:
                w = row.index("inf") if "inf" in row else cols
                if any(v != "inf" for v in row[w:]) or (widths and w < widths[-1]):
                    raise ValueError('"inf" must form a one-sided staircase')
                widths.append(w)
            if widths[-1] == 0:
                raise ValueError("pairwise costs must have a finite entry")

            # 横差分を下から引き継ぐ。全成分が禁止の行は直下の行をコピーする。
            for a in range(rows - 1, -1, -1):
                row = costs[a]
                if widths[a] == 0:
                    costs[a] = costs[a + 1].copy()
                    continue
                for b in range(widths[a], cols):
                    delta = costs[a + 1][b] - costs[a + 1][b - 1] if a + 1 < rows else 0
                    row[b] = row[b - 1] + delta

        # 各行の横差分が下の行ほど小さいことが Monge 条件。追加前に検査する。
        for a in range(1, rows):
            prev, curr = costs[a - 1], costs[a]
            assert all(prev[b] - prev[b - 1] >= curr[b] - curr[b - 1]
                       for b in range(1, cols)), "pairwise costs must be Monge"

        if widths:
            # 幅が増える境界ごとに x_j >= 旧幅 ⇒ x_i >= a を課す。
            for a in range(1, rows):
                w = widths[a - 1]
                if w < widths[a]:
                    if w == 0:
                        self._cut.force(self._threshold(i, a), True)
                    else:
                        self.add_if_ge_then_ge(j, w, i, a)
            if widths[-1] < cols:
                self._cut.force(self._threshold(j, widths[-1]), False)

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
