# competitive-verifier: STANDALONE

from random import Random

from python.graph.minimum_distance.FloydWarshall import FloydWarshall


def brute_dist(n, edges):
    d = [[FloydWarshall.INF]*n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0
    for u,v,w in edges:
        d[u][v] = min(d[u][v],w)
    for k in range(n):
        d = [[min(d[i][j],d[i][k]+d[k][j]) for j in range(n)] for i in range(n)]
    return d


if __name__ == "__main__":
    rng = Random(81)
    for undirected in [False,True]:
        for n in range(1,8):
            f = FloydWarshall(n)
            edges = []
            for _ in range(n*2):
                u,v,w = rng.randrange(n),rng.randrange(n),rng.randrange(10)
                edges.append((u,v,w))
                f.add_edge(u,v,w)
                if undirected:
                    edges.append((v,u,w))
                    f.add_edge(v,u,w)
            f.build()
            assert f.D == brute_dist(n,edges)
            for _ in range(20):
                u,v,w = rng.randrange(n),rng.randrange(n),rng.randrange(10)
                edges.append((u,v,w))
                if undirected:
                    edges.append((v,u,w))
                    f.construct_edge_undirected(u,v,w)
                else:
                    f.construct_edge_directed(u,v,w)
                assert f.D == brute_dist(n,edges)

    # 有向グラフに無向辺を追加する。片方向のみ距離が改善する場合も含む。
    f = FloydWarshall(2)
    f.add_edge(0,1,1)
    f.build()
    f.construct_edge_undirected(0,1,3)
    assert f.D == [[0,1],[3,0]]
    for n in range(1,8):
        for _ in range(30):
            f = FloydWarshall(n)
            edges = [(rng.randrange(n),rng.randrange(n),rng.randrange(10)) for _ in range(n*2)]
            for u,v,w in edges:
                f.add_edge(u,v,w)
            f.build()
            for _ in range(20):
                u,v,w = rng.randrange(n),rng.randrange(n),rng.randrange(10)
                edges.extend([(u,v,w),(v,u,w)])
                f.construct_edge_undirected(u,v,w)
                assert f.D == brute_dist(n,edges)
