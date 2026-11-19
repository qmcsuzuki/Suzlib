# competitive-verifier: TITLE 割り当て問題


def _assignment(
    cost: list[list[int]],
    flow: int | None = None,
    full: bool = False,
) -> tuple[list[int], list[int]]:
    n = len(cost)
    m = len(cost[0]) if n else 0
    assert all(len(row) == m for row in cost)

    if flow is None:
        flow = min(n, m)
    assert 0 <= flow <= min(n, m)
    if flow == 0:
        return [0], [-1] * n

    # full モードでは、左頂点を1個ずつ追加できるよう n <= m に揃える。
    transposed = full and n > m
    if transposed:
        cost = [list(row) for row in zip(*cost)]
        n, m = m, n

    left_match = [-1] * n
    right_match = [-1] * m
    costs = [0]

    # reduced cost = cost[i][j] + left_potential[i] - right_potential[j]
    # full モードでは、追加する左頂点のポテンシャルを逐次初期化する。
    # それ以外では、全ての未使用右頂点の sink 辺を tight に保つ。
    left_potential = [0] * n
    right_potential = [0 if full else min(min(row) for row in cost)] * m
    total_cost = 0

    if not full:
        # 未マッチ左頂点のポテンシャルは常に共通値 free_potential。
        # 列 j ごとに左頂点を費用昇順に並べ、未マッチの最小を指すポインタを持つ。
        # 左頂点は一度マッチすると未マッチに戻らないので、ポインタは単調に進む。
        free_potential = 0
        order = [
            sorted(range(n), key=col.__getitem__) for col in zip(*cost)
        ]
        ptr = [0] * m

    for k in range(flow):
        used_right = [False] * m

        if full:
            # 行追加型 Hungarian 法。既存のマッチングは先頭 k 行だけを使う。
            i = k
            row = cost[i]
            potential_i = max(right_potential[j] - row[j] for j in range(m))
            left_potential[i] = potential_i
            dist = [row[j] + potential_i - right_potential[j] for j in range(m)]
            prev_left = [i] * m
        else:
            # 任意流量では全ての未マッチ左頂点を始点とする。
            # 各列について、未マッチ左頂点からの最小 reduced cost で初期化する。
            dist = [0] * m
            prev_left = [0] * m
            for j in range(m):
                order_j = order[j]
                p = ptr[j]
                while left_match[order_j[p]] != -1:
                    p += 1
                ptr[j] = p
                i = order_j[p]
                prev_left[j] = i
                dist[j] = cost[i][j] + free_potential - right_potential[j]

        while True:
            v = -1
            best = 0
            for j in range(m):
                if used_right[j]:
                    continue
                if v == -1 or dist[j] < best:
                    best = dist[j]
                    v = j

            used_right[v] = True

            if right_match[v] == -1:
                target = v
                shortest = best
                break

            # matched edge の逆辺は reduced cost 0。
            i = right_match[v]
            row = cost[i]
            base = best + left_potential[i]

            for j in range(m):
                if used_right[j]:
                    continue
                nd = base + row[j] - right_potential[j]
                if nd < dist[j]:
                    dist[j] = nd
                    prev_left[j] = i

        # shortest path 上の辺を tight にし、全 residual edge の
        # reduced cost の非負性を保つ。
        if full:
            left_potential[k] -= shortest
        else:
            free_potential -= shortest

        for j in range(m):
            if not used_right[j]:
                continue
            shift = dist[j] - shortest
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
            elif not full:
                # 始点の左頂点が新たにマッチする。
                left_potential[i] = free_potential
            left_match[i] = j
            right_match[j] = i
            j = old_j

        costs.append(total_cost)

    if transposed:
        original_match = [-1] * m
        for i, j in enumerate(left_match):
            if j != -1:
                original_match[j] = i
        left_match = original_match
    return costs, left_match


def assignment(
    cost: list[list[int]],
    flow: int | None = None,
) -> tuple[int, list[int]]:
    """完全二部グラフの最小費用割り当てを求める。負の費用に対応する。
    戻り値は (最小費用, match), match[i] = i に対応する頂点（-1 は対応無し）

    - cost[i][j]: 左頂点 i と右頂点 j を対応させる費用
    - flow=None または flow=min(n, m) では Hungarian 法で min(n, m) 個を対応させる
    - flow を指定した場合はちょうど flow 個を対応させる
    - 計算量: O(min(n, m)^2 max(n, m))、flow 指定時は O(nm log n + flow^2 m)
    """
    n = len(cost)
    full = flow is None or flow == min(n, len(cost[0]) if n else 0)
    costs, match = _assignment(cost, flow, full=full)
    return costs[-1], match


def assignment_costs(
    cost: list[list[int]],
    flow: int | None = None,
) -> list[int]:
    """各流量 0,1,...,flow に対する最小割り当て費用の配列 costs を返す。負の費用と長方形行列に対応する。

    計算量: O(nm log n + flow^2 m)
    """
    costs, _ = _assignment(cost, flow)
    return costs
