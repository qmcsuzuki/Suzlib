# competitive-verifier: TITLE 凸折れ線費用の最小費用テンション

from collections.abc import Callable, Sequence

from python.graph.flow.mincostflow.MinCostBFlow import MinCostBFlow


class MinCostTension:
    """整数電位に対し、差 x = p[v]-p[u] の上下限制約下で費用の総和を最小化する。

    入力は整数。solve は一度だけ呼び、成功後は potentials で最適電位を取得できる。
    dag はキーワード引数で必ず指定する。dag=True は上下限・費用を展開した双対辺が DAG のときに指定する。
    上限とヒンジは u→v、下限は v→u の辺を作る。線形項は辺を作らない。
    構築は双対辺数に線形。求解は MinCostBFlow 一回と、成功時の
    電位取得・上下限検査 O(n + 制約辺数)。空間は O(n + 双対辺数)。
    """

    def __init__(self, n: int, *, dag: bool) -> None:
        self._flow = MinCostBFlow(n, dag=dag)
        self._balance = [0] * n
        self._bounds: list[tuple[int, int, int]] = []
        self._capacity = 0
        self._constant = 0
        self._solved = False
        self._potential: list[int] | None = None

    def add_bounds(self, u: int, v: int, lower: int | None = None,
                   upper: int | None = None) -> None:
        """lower <= x <= upper を課す。None は片側の制約なし。"""
        assert not self._solved
        assert 0 <= u < len(self._balance) and 0 <= v < len(self._balance)
        if lower is not None:
            self._bounds.append((v, u, -lower))
        if upper is not None:
            self._bounds.append((u, v, upper))

    def add_linear(self, u: int, v: int, cost: int) -> None:
        """cost * x を加える。"""
        assert not self._solved
        assert 0 <= u < len(self._balance) and 0 <= v < len(self._balance)
        self._balance[u] -= cost
        self._balance[v] += cost

    def add_hinge(self, u: int, v: int, a: int, weight: int) -> None:
        """weight * max(0, x-a) を加える。"""
        assert not self._solved and weight >= 0
        if weight:
            self._flow.add_edge(u, v, 0, weight, a)
            self._capacity += weight

    def add_abs(self, u: int, v: int, a: int, weight: int) -> None:
        """weight * abs(x-a) を加える。双対辺は両方向に一本ずつ。"""
        self.add_hinge(u, v, a, weight)
        self.add_hinge(v, u, -a, weight)

    def add_piecewise_linear(self, u: int, v: int, breakpoints: Sequence[int],
                             slopes: Sequence[int], value_at_zero: int = 0) -> None:
        """昇順の折れ点、各区間の傾き、x=0 の値から凸折れ線費用を加える。"""
        assert len(slopes) == len(breakpoints) + 1
        assert all(a < b for a, b in zip(breakpoints, breakpoints[1:]))
        assert all(a <= b for a, b in zip(slopes, slopes[1:]))
        self.add_linear(u, v, slopes[0])
        self._constant += value_at_zero
        for i, a in enumerate(breakpoints):
            jump = slopes[i + 1] - slopes[i]
            self.add_hinge(u, v, a, jump)
            self._constant -= jump * max(0, -a)

    def add_discrete_convex(self, u: int, v: int, lower: int, upper: int,
                            f: Callable[[int], int]) -> None:
        """lower <= x <= upper を課し、整数上の凸費用 f(x) を加える。O(upper-lower+1)。"""
        assert lower <= upper
        values = [f(x) for x in range(lower, upper + 1)]
        slopes = [b - a for a, b in zip(values, values[1:])]
        assert all(a <= b for a, b in zip(slopes, slopes[1:]))
        self.add_bounds(u, v, lower, upper)
        self._constant += values[0]
        if slopes:
            self.add_linear(u, v, slopes[0])
            self._constant -= lower * slopes[0]
            for i in range(1, len(slopes)):
                self.add_hinge(u, v, lower + i, slopes[i] - slopes[i - 1])

    def solve(self) -> int | None:
        """最小費用を返す。制約矛盾または下に非有界なら None。"""
        assert not self._solved
        self._solved = True
        # ヒンジ辺の流量を固定し、制約辺上の循環を除くと各流量は cap 未満。
        cap = 1 + self._capacity + sum(max(0, b) for b in self._balance)
        for v, b in enumerate(self._balance):
            self._flow.add_balance(v, b)
        for u, v, cost in self._bounds:
            self._flow.add_edge(u, v, 0, cap, cost)
        ok, cost = self._flow.solve()
        if not ok:
            return None
        p = self._flow.potential()
        # 制約が整合するなら全制約辺が未飽和の最適解が存在し、
        # 相補性により任意の最適電位が元の上下限を満たす。
        if any(p[v] - p[u] > limit for u, v, limit in self._bounds):
            return None
        self._potential = p
        return self._constant - cost

    def potentials(self) -> list[int]:
        """有限最適値が得られた後、最適電位のコピーを返す。O(n)。"""
        assert self._potential is not None
        return self._potential.copy()
