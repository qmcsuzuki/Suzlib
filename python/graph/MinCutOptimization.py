# competitive-verifier: TITLE Min Cut Optimization（燃やす埋める）

from python.graph.MaxFlow import MFGraph


class MinCutOptimization:
    """s-t 最小カットで解ける 0/1 最適化問題を構築する。"""

    def __init__(self, n: int) -> None:
        """n 個の bool 変数 x_0, ..., x_{n-1} を持つ問題を初期化する。"""
        assert 0 <= n
        self._n = n
        self._s = n
        self._t = n + 1
        self._graph = MFGraph(n + 2)

        self._cost_false = [0] * n
        self._cost_true = [0] * n
        self._offset = 0

        self._finite_cap_sum = 0
        self._hard_edges: list[tuple[int, int]] = []
        self._solved = False

    def _check_variable(self, i: int) -> None:
        assert 0 <= i < self._n
        assert not self._solved

    def add_unary(self, i: int, cost_false: int, cost_true: int) -> None:
        """x_i=False / True のときのコストをそれぞれ加える。"""
        self._check_variable(i)
        self._cost_false[i] += cost_false
        self._cost_true[i] += cost_true

    def add_cost_true(self, i: int, cost: int) -> None:
        """x_i=True のとき cost を加える。"""
        self._check_variable(i)
        self._cost_true[i] += cost

    def add_cost_false(self, i: int, cost: int) -> None:
        """x_i=False のとき cost を加える。"""
        self._check_variable(i)
        self._cost_false[i] += cost

    def add_penalty(self, i: int, j: int, cost: int) -> None:
        """x_i=True, x_j=False のとき cost を加える。"""
        self._check_variable(i)
        self._check_variable(j)
        assert 0 <= cost
        if i == j or cost == 0:
            return
        self._graph.add_edge(i, j, cost)
        self._finite_cap_sum += cost

    def add_pairwise(
        self,
        i: int,
        j: int,
        cost_ff: int,
        cost_ft: int,
        cost_tf: int,
        cost_tt: int,
    ) -> None:
        """(x_i, x_j) ごとの submodular な 2 変数コストを加える。

        cost_ff + cost_tt <= cost_ft + cost_tf を仮定する。
        """
        self._check_variable(i)
        self._check_variable(j)
        assert i != j
        penalty = cost_ft + cost_tf - cost_ff - cost_tt
        assert 0 <= penalty

        self._offset += cost_ff
        self._cost_true[i] += cost_tt - cost_ft
        self._cost_true[j] += cost_ft - cost_ff
        if penalty:
            self._graph.add_edge(i, j, penalty)
            self._finite_cap_sum += penalty

    def add_implication(self, i: int, j: int) -> None:
        """x_i=True なら x_j=True を強制する。"""
        self._check_variable(i)
        self._check_variable(j)
        if i != j:
            self._hard_edges.append((i, j))

    def force(self, i: int, value: bool) -> None:
        """x_i=value を強制する。"""
        self._check_variable(i)
        assert value in (False, True)
        if value:
            self._hard_edges.append((self._s, i))
        else:
            self._hard_edges.append((i, self._t))

    def solve(self) -> tuple[int, list[bool]]:
        """最小コストと、それを達成する bool 変数の割り当てを返す。

        hard constraint が両立しない場合は ValueError を送出する。
        """
        assert not self._solved
        self._solved = True

        finite_cap_sum = self._finite_cap_sum
        offset = self._offset

        for i in range(self._n):
            cost_false = self._cost_false[i]
            cost_true = self._cost_true[i]
            base = min(cost_false, cost_true)
            offset += base
            cost_false -= base
            cost_true -= base

            if cost_false:
                self._graph.add_edge(self._s, i, cost_false)
                finite_cap_sum += cost_false
            if cost_true:
                self._graph.add_edge(i, self._t, cost_true)
                finite_cap_sum += cost_true

        inf = finite_cap_sum + 1
        for src, dst in self._hard_edges:
            self._graph.add_edge(src, dst, inf)

        cut_cost = self._graph.flow(self._s, self._t)
        if cut_cost >= inf:
            raise ValueError("hard constraints are infeasible")

        assignment = self._graph.min_cut(self._s)[: self._n]
        return offset + cut_cost, assignment
