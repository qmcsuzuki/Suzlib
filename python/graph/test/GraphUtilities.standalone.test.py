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
