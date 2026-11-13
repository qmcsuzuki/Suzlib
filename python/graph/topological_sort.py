# competitive-verifier: TITLE トポロジカルソート（入次数法）

def topological_sort(g):
    """有向グラフの隣接リスト g からトポロジカル順を一つ返す。閉路があれば None。
    時間 O(V + E)、補助空間 O(V)。
    """
    indegree = [0] * len(g)
    for neighbors in g:
        for v in neighbors:
            indegree[v] += 1

    order = [v for v in range(len(g)) if indegree[v] == 0]
    # order をキューと兼用し、末尾に追加した頂点も順に処理する。
    for u in order:
        for v in g[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                order.append(v)
    return order if len(order) == len(g) else None
