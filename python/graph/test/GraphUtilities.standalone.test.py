# competitive-verifier: STANDALONE

from random import Random

from python.graph.minimum_distance.FloydWarshall import FloydWarshall
from python.graph.tree.RootedTreeHash import rooted_tree_hash
from python.graph.tree.TreeBasic import get_order_and_parent
from python.graph.grid.LargeGridUF import LargeGridUF


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
    assert rooted_tree_hash([[1],[0]],0)[0] != rooted_tree_hash([[1],[0]],0)[1]
    for n in range(1,30):
        g = [[] for _ in range(n)]
        for v in range(1,n):
            p = rng.randrange(v)
            g[p].append(v)
            g[v].append(p)
        root = rng.randrange(n)
        order, par = get_order_and_parent(g,root)
        actual = rooted_tree_hash(g,root)
        expected = rooted_tree_hash(g,root,par,order)
        assert all((actual[i] == actual[j]) == (expected[i] == expected[j])
                   for i in range(n) for j in range(n))
    uf, blocks = LargeGridUF(2,3,[])
    assert uf.issame(blocks[0][0] % (1 << 20), blocks[1][0] % (1 << 20))
