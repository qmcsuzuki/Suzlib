# competitive-verifier: TITLE Dial法（非負整数重み単一始点最短路）

def Dial(g, Wmax, start):
    """
    Dial's algorithm (circular buckets), O(Wmax * V + E)
    Wmax: 辺のコストの最大値
    """
    n = len(g)
    C = Wmax + 1
    INF = 1<<60
    dist = [INF]*n
    dist[start] = 0

    buckets = [[] for _ in range(C)]
    buckets[0].append(start)
    pending = 1  # バケット内の要素数

    idx = 0  # 現在見ているバケット index
    d = 0    # 現在の距離（idx と同期して増える）

    while pending:
        # 次の非空バケットまで進める
        while not buckets[idx]:
            idx += 1
            if idx == C: idx = 0
            d += 1
        v = buckets[idx].pop()
        pending -= 1
        if dist[v] != d:
            continue

        for to, cost in g[v]:
            nd = d + cost
            if nd < dist[to]:
                dist[to] = nd
                j = idx + cost
                if j >= C: j -= C
                buckets[j].append(to)
                pending += 1

    return dist
