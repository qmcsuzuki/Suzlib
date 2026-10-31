# competitive-verifier: STANDALONE

from itertools import product
from random import Random

from python.graph.flow.MinCutOptimization import MinCutOptimization


def brute_force(
    n,
    unary,
    pairwise,
    penalties,
    implications,
    forces,
):
    best = None
    best_x = None
    for x in product([False, True], repeat=n):
        if any(x[i] and not x[j] for i, j in implications):
            continue
        if any(x[i] != value for i, value in forces):
            continue

        cost = 0
        for i in range(n):
            cost += unary[i][x[i]]
        for i, j, costs in pairwise:
            cost += costs[(x[i] << 1) | x[j]]
        for i, j, penalty in penalties:
            if x[i] and not x[j]:
                cost += penalty

        if best is None or cost < best:
            best = cost
            best_x = x
    return best, best_x


def evaluate(x, unary, pairwise, penalties):
    cost = 0
    for i in range(len(x)):
        cost += unary[i][x[i]]
    for i, j, costs in pairwise:
        cost += costs[(x[i] << 1) | x[j]]
    for i, j, penalty in penalties:
        if x[i] and not x[j]:
            cost += penalty
    return cost


if __name__ == "__main__":
    rng = Random(91)

    for _ in range(1000):
        n = rng.randint(1, 6)
        opt = MinCutOptimization(n)

        unary = [[0, 0] for _ in range(n)]
        pairwise = []
        penalties = []
        implications = []
        forces = []

        for i in range(n):
            cost_false = rng.randint(-5, 5)
            cost_true = rng.randint(-5, 5)
            opt.add_unary(i, cost_false, cost_true)
            unary[i][0] += cost_false
            unary[i][1] += cost_true

            if rng.randrange(2):
                cost = rng.randint(-3, 3)
                opt.add_cost_true(i, cost)
                unary[i][1] += cost
            if rng.randrange(2):
                cost = rng.randint(-3, 3)
                opt.add_cost_false(i, cost)
                unary[i][0] += cost

        for i in range(n):
            for j in range(i + 1, n):
                if rng.randrange(3) == 0:
                    offset = rng.randint(-3, 3)
                    a = rng.randint(-3, 3)
                    b = rng.randint(-3, 3)
                    penalty = rng.randint(0, 5)
                    costs = (
                        offset,
                        offset + b,
                        offset + a + penalty,
                        offset + a + b,
                    )
                    opt.add_pairwise(i, j, *costs)
                    pairwise.append((i, j, costs))

                if rng.randrange(5) == 0:
                    penalty = rng.randint(0, 5)
                    opt.add_penalty(i, j, penalty)
                    penalties.append((i, j, penalty))

                if rng.randrange(8) == 0:
                    opt.add_implication(i, j)
                    implications.append((i, j))
                if rng.randrange(10) == 0:
                    opt.add_implication(j, i)
                    implications.append((j, i))

        for i in range(n):
            if rng.randrange(12) == 0:
                value = bool(rng.randrange(2))
                opt.force(i, value)
                forces.append((i, value))

        expected, _ = brute_force(
            n,
            unary,
            pairwise,
            penalties,
            implications,
            forces,
        )

        if expected is None:
            try:
                opt.solve()
            except ValueError:
                pass
            else:
                assert False
            continue

        actual, x = opt.solve()
        assert actual == expected
        assert evaluate(x, unary, pairwise, penalties) == expected
        assert all(not x[i] or x[j] for i, j in implications)
        assert all(x[i] == value for i, value in forces)

    # Non-submodular pairwise costs cannot be represented by an s-t cut.
    opt = MinCutOptimization(2)
    try:
        opt.add_pairwise(0, 1, 0, 0, 0, 1)
    except AssertionError:
        pass
    else:
        assert False

    def check_auto(n, unary, pairwise, penalties=(), implications=(), forces=()):
        opt = MinCutOptimization(n, auto_flip=True)
        for i, (c0, c1) in enumerate(unary):
            opt.add_cost_false(i, c0)
            opt.add_cost_true(i, c1)
        tables = {}
        for i, j, costs in pairwise:
            opt.add_pairwise(i, j, *costs)
            if i > j:
                i, j = j, i
                costs = [costs[0], costs[2], costs[1], costs[3]]
            total = tables.setdefault((i, j), [0] * 4)
            for k in range(4):
                total[k] += costs[k]
        for i, j, cost in penalties:
            opt.add_penalty(i, j, cost)
            if i != j:
                key = (min(i, j), max(i, j))
                tables.setdefault(key, [0] * 4)[2 if i < j else 1] += cost
        for i, j in implications:
            opt.add_implication(i, j)
        for i, value in forces:
            opt.force(i, value)

        # 反転の全候補について、変換した表の劣モジュラ性を直接確認する。
        representable = False
        for flip in product(range(2), repeat=n):
            if any(flip[i] != flip[j] for i, j in implications):
                continue
            valid = True
            for (i, j), costs in tables.items():
                transformed = [costs[((a ^ flip[i]) << 1) | (b ^ flip[j])]
                               for a, b in product(range(2), repeat=2)]
                if transformed[0] + transformed[3] > transformed[1] + transformed[2]:
                    valid = False
                    break
            if valid:
                representable = True
                break
        expected, _ = brute_force(n, unary, pairwise, penalties, implications, forces)
        if not representable or expected is None:
            message = ("hard constraints are infeasible" if representable else
                       "auto-flip constraints are inconsistent")
            try:
                opt.solve()
            except ValueError as exc:
                assert str(exc) == message
            else:
                assert False
            return
        actual, x = opt.solve()
        assert len(x) == n and all(type(v) is bool for v in x)
        assert actual == expected
        assert evaluate(x, unary, pairwise, penalties) == expected
        assert all(not x[i] or x[j] for i, j in implications)
        assert all(x[i] == value for i, value in forces)

    check_auto(0, [], [])
    # 合算前は反転条件が矛盾する。逆順登録と penalty の相殺も含む。
    check_auto(2, [[0, 2], [3, 0]],
               [(0, 1, [0, 0, 3, 0]), (1, 0, [0, 0, 0, 1])])
    check_auto(2, [[0, 2], [3, 0]], [(1, 0, [0, 0, -5, 0])],
               [(1, 0, 5)])
    # 逆 Monge の奇数閉路は反転不能。偶数閉路は可能。
    for n in (3, 4):
        check_auto(n, [[0, 0] for _ in range(n)],
                   [(i, (i + 1) % n, [1, 0, 0, 1]) for i in range(n)])
    # 頂点 1, 2 が反転され、含意の向きと force の値が変わる。
    check_auto(3, [[0, 0]] * 3,
               [(0, 1, [2, 0, 0, 2]), (0, 2, [2, 0, 0, 2])],
               implications=[(1, 2)], forces=[(1, True), (2, False)])
    check_auto(3, [[0, 0]] * 3,
               [(0, 1, [2, 0, 0, 2]), (0, 2, [2, 0, 0, 2])],
               implications=[(1, 2)], forces=[(1, True)])
    check_auto(2, [[0, 0]] * 2, [(0, 1, [1, 0, 0, 1])],
               implications=[(0, 1)])
    check_auto(1, [[0, 0]], [], [(0, 0, 3)], [(0, 0)],
               [(0, False), (0, True)])

    for _ in range(1500):
        n = rng.randint(1, 6)
        unary = [[rng.randint(-5, 5), rng.randint(-5, 5)] for _ in range(n)]
        pairwise = []
        penalties = []
        implications = []
        forces = []
        # 半分は既知の反転を持つ問題、残りは任意のコスト表。
        planted = rng.randrange(2)
        flip = [rng.randrange(2) for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if rng.randrange(2):
                    costs = [rng.randint(-6, 6) for _ in range(4)]
                    if planted:
                        costs[3] = costs[1] + costs[2] - costs[0] - rng.randrange(6)
                        mask = (flip[i] << 1) | flip[j]
                        costs = [costs[k ^ mask] for k in range(4)]
                    # 非劣モジュラな項への分割も許されることを検証。
                    part = [rng.randint(-8, 8) for _ in range(4)]
                    rest = [costs[k] - part[k] for k in range(4)]
                    pairwise.append((i, j, part))
                    pairwise.append((j, i, [rest[0], rest[2], rest[1], rest[3]]))
                if not planted or flip[i] == flip[j]:
                    if rng.randrange(5) == 0:
                        penalties.append((j, i, rng.randrange(6)))
                    if rng.randrange(7) == 0:
                        implications.append((j, i))
            if rng.randrange(5) == 0:
                forces.append((i, bool(rng.randrange(2))))
        check_auto(n, unary, pairwise, penalties, implications, forces)
