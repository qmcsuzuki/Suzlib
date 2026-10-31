# competitive-verifier: TITLE Min Cut Optimization（燃やす埋める）

from python.graph.flow.MaxFlow import MFGraph


class MinCutOptimization:
    """s-t 最小カットで解ける 0/1 最適化問題を構築する。

    auto_flip=True では同じ頂点対の有限コストを合算し、変数の反転で
    劣モジュラ化する。入力・返り値はすべて元の変数の意味で指定する。
    合算後の各項と各含意を共通の反転で表現できる場合に対応する。
    force による変数消去や、含意を使ったコストの簡約は行わない。
    異なる頂点対数と含意数の合計を M として、反転判定は時間・空間
    O(n + M)。別途、構築したグラフで最大流を計算する。

    例: opt = MinCutOptimization(2, auto_flip=True)
        opt.add_pairwise(0, 1, 1, 0, 0, 1)  # 異なる値を好む項
        cost, x = opt.solve()  # cost == 0, x[0] != x[1]
    """

    def __init__(self, n: int, auto_flip: bool = False) -> None:
        """n 個の bool 変数 x_0, ..., x_{n-1} を持つ問題を初期化する。"""
        assert 0 <= n
        self._auto_flip = auto_flip
        self._pair_costs: dict[tuple[int, int], list[int]] = {}
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
        if self._auto_flip:
            self.add_pairwise(i, j, 0, 0, cost, 0)
        else:
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
        """(x_i, x_j) ごとの 2 変数コストを加える (i != j)。

        既定では cost_ff + cost_tt <= cost_ft + cost_tf を要求する。
        auto_flip=True では add_penalty も含め頂点対ごとに合算し、
        solve() で反転の可否を判定する。登録は平均 O(1)。
        """
        self._check_variable(i)
        self._check_variable(j)
        assert i != j
        if self._auto_flip:
            if i > j:
                i, j = j, i
                cost_ft, cost_tf = cost_tf, cost_ft
            key = (i, j)
            if key not in self._pair_costs:
                self._pair_costs[key] = [cost_ff, cost_ft, cost_tf, cost_tt]
            else:
                costs = self._pair_costs[key]
                costs[0] += cost_ff
                costs[1] += cost_ft
                costs[2] += cost_tf
                costs[3] += cost_tt
        else:
            self._add_submodular(i, j, cost_ff, cost_ft, cost_tf, cost_tt)

    def _add_submodular(self, i, j, cost_ff, cost_ft, cost_tf, cost_tt):
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

    def _prepare_auto_flip(self) -> list[int]:
        n = self._n
        adjacency = [[] for _ in range(n)]
        for (i, j), (ff, ft, tf, tt) in self._pair_costs.items():
            delta = ft + tf - ff - tt
            if delta:
                parity = int(delta < 0)
                adjacency[i].append((j, parity))
                adjacency[j].append((i, parity))
        for i, j in self._hard_edges:
            if i < n and j < n:
                adjacency[i].append((j, 0))
                adjacency[j].append((i, 0))

        flip = [-1] * n
        for root in range(n):
            if flip[root] != -1:
                continue
            flip[root] = 0
            stack = [root]
            while stack:
                i = stack.pop()
                for j, parity in adjacency[i]:
                    value = flip[i] ^ parity
                    if flip[j] == -1:
                        flip[j] = value
                        stack.append(j)
                    elif flip[j] != value:
                        raise ValueError("auto-flip constraints are inconsistent")

        # 単変数項を先に変換し、その後で変換済みの 2 変数項を分解する。
        for i in range(n):
            if flip[i]:
                self._cost_false[i], self._cost_true[i] = (
                    self._cost_true[i], self._cost_false[i]
                )
        for (i, j), costs in self._pair_costs.items():
            mask = (flip[i] << 1) | flip[j]
            self._add_submodular(
                i, j, costs[mask], costs[1 ^ mask],
                costs[2 ^ mask], costs[3 ^ mask],
            )
        self._pair_costs.clear()

        for k, (i, j) in enumerate(self._hard_edges):
            if i == self._s:
                if flip[j]:
                    self._hard_edges[k] = (j, self._t)
            elif j == self._t:
                if flip[i]:
                    self._hard_edges[k] = (self._s, i)
            elif flip[i]:
                self._hard_edges[k] = (j, i)
        return flip

    def solve(self) -> tuple[int, list[bool]]:
        """最小コストと、それを達成する bool 変数の割り当てを返す。

        呼び出しは 1 回のみ。以後の追加も不可。
        auto_flip=True で反転条件が矛盾すると ValueError
        ("auto-flip constraints are inconsistent")。これは元の問題の
        実行不能を意味しない。反転可能でも hard constraint が両立しない
        場合は ValueError ("hard constraints are infeasible")。
        """
        assert not self._solved
        self._solved = True
        flip = self._prepare_auto_flip() if self._auto_flip else []

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
        if self._auto_flip:
            for i in range(self._n):
                if flip[i]:
                    assignment[i] = not assignment[i]
        return offset + cut_cost, assignment
