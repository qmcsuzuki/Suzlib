# competitive-verifier: TITLE 割り当て問題


def _assignment(
    cost: list[list[int]],
    flow: int | None = None,
) -> tuple[list[int], list[int]]:
    n = len(cost)
    m = len(cost[0]) if n else 0
    assert all(len(row) == m for row in cost)

    if flow is None:
        flow = min(n, m)
    assert 0 <= flow <= min(n, m)

    left_match = [-1] * n
    costs = [0]
    if flow == 0:
        return costs, left_match

    right_match = [-1] * m

    # reduced cost = cost[i][j] + left_potential[i] - right_potential[j]
    # が非負になる初期ポテンシャル。全ての未使用右頂点の sink 辺を
    # tight に保つため、右側には共通の値を入れる。
    min_cost = min(min(row) for row in cost)
    left_potential = [0] * n
    right_potential = [min_cost] * m
    total_cost = 0

    for _ in range(flow):
        dist: list[int | None] = [None] * m
        prev_left = [-1] * m
        used_right = [False] * m
        free_left = []

        # 仮想 source から全ての未使用左頂点への辺は常に tight。
        # それらを距離 0 の始点として右側への辺を一度に緩和する。
        for i in range(n):
            if left_match[i] != -1:
                continue
            free_left.append(i)
            row = cost[i]
            potential_i = left_potential[i]
            for j in range(m):
                nd = row[j] + potential_i - right_potential[j]
                if dist[j] is None or nd < dist[j]:
                    dist[j] = nd
                    prev_left[j] = i

        while True:
            v = -1
            best: int | None = None
            for j in range(m):
                if used_right[j] or dist[j] is None:
                    continue
                if best is None or dist[j] < best:
                    best = dist[j]
                    v = j

            assert v != -1
            used_right[v] = True

            if right_match[v] == -1:
                target = v
                shortest = dist[v]
                assert shortest is not None
                break

            # matched edge の逆辺は reduced cost 0。
            i = right_match[v]
            row = cost[i]
            potential_i = left_potential[i]
            dist_i = dist[v]
            assert dist_i is not None

            for j in range(m):
                if used_right[j]:
                    continue
                nd = dist_i + row[j] + potential_i - right_potential[j]
                if dist[j] is None or nd < dist[j]:
                    dist[j] = nd
                    prev_left[j] = i

        # shortest path 上の辺を tight にし、全 residual edge の
        # reduced cost の非負性を保つ。
        for i in free_left:
            left_potential[i] -= shortest

        for j in range(m):
            if not used_right[j]:
                continue
            dist_j = dist[j]
            assert dist_j is not None
            shift = dist_j - shortest
            right_potential[j] += shift
            i = right_match[j]
            if i != -1:
                left_potential[i] += shift

        # target から交互路を逆にたどって matching を 1 増やす。
        j = target
        while j != -1:
            i = prev_left[j]
            old_j = left_match[i]
            total_cost += cost[i][j]
            if old_j != -1:
                total_cost -= cost[i][old_j]
            left_match[i] = j
            right_match[j] = i
            j = old_j

        costs.append(total_cost)

    return costs, left_match


def assignment(
    cost: list[list[int]],
    flow: int | None = None,
) -> tuple[int, list[int]]:
    """完全二部グラフの最小費用割り当てを求める。

    cost[i][j] を左頂点 i と右頂点 j を対応させる費用とする。
    flow=None では min(n, m) 個、flow を指定した場合はちょうど flow 個を対応させる。
    戻り値は (最小費用, match) で、match[i] は i に対応する右頂点、
    未使用の左頂点では -1 である。

    負の費用と長方形行列に対応する。
    計算量は O(flow * n * m)、追加メモリは O(n + m)。
    """
    costs, match = _assignment(cost, flow)
    return costs[-1], match


def assignment_costs(
    cost: list[list[int]],
    flow: int | None = None,
) -> list[int]:
    """各流量に対する最小割り当て費用を返す。

    戻り値 costs は costs[f] がちょうど f 個を対応させる最小費用である。
    flow=None では f=0,...,min(n,m)、flow を指定した場合は f=0,...,flow を返す。

    負の費用と長方形行列に対応する。
    計算量は O(flow * n * m)、追加メモリは O(n + m)。
    """
    costs, _ = _assignment(cost, flow)
    return costs
