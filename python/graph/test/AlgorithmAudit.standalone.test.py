# competitive-verifier: STANDALONE

from itertools import product
from random import Random

from python.graph.MinCostFlow import MCFGraph, DAGMCFGraph
from python.graph.SCC import find_SCC
from python.graph.BipartiteMatching import BipartiteMatching
from python.graph.BipartiteMatchingStructure import matching_structure, NEVER, SOMETIMES, ALWAYS
from python.graph.DirectedTrailDecomposition import DirectedTrailDecomposition
from python.graph.UndirectedTrailDecomposition import UndirectedTrailDecomposition


def brute_flow(n,edges,s,t):
    costs = {}
    for flows in product(*(range(cap+1) for _,_,cap,_ in edges)):
        balance = [0]*n
        cost = 0
        for (u,v,_,c),f in zip(edges,flows):
            balance[u] -= f
            balance[v] += f
            cost += c*f
        f = balance[t]
        if f < 0 or balance[s] != -f or any(balance[v] for v in range(n) if v not in (s,t)):
            continue
        costs[f] = min(costs.get(f,cost),cost)
    return costs


def check_slope(slope,expected):
    assert slope[0] == (0,0) and slope[-1][0] == max(expected)
    for (a,ca),(b,cb) in zip(slope,slope[1:]):
        assert a < b and (cb-ca) % (b-a) == 0
        for f in range(a,b+1):
            assert ca + (cb-ca)//(b-a)*(f-a) == expected[f]


def minimum_trails(n,edges,directed):
    parent = list(range(n))
    def leader(v):
        while parent[v] != v: v = parent[v]
        return v
    diff = [0]*n
    active = set()
    for u,v in edges:
        parent[leader(u)] = leader(v)
        active.update([u,v])
        diff[u] += 1
        diff[v] += -1 if directed else 1
    groups = {}
    for v in active:
        groups.setdefault(leader(v),[]).append(v)
    return sum(max(1,sum(max(0,diff[v]) for v in vs) if directed
                   else sum(diff[v] & 1 for v in vs)//2) for vs in groups.values())


if __name__ == '__main__':
    rng = Random(20261002)
    # 容量と全辺の流量を列挙した独立な最小費用オラクル。
    for _ in range(300):
        n = rng.randrange(2,6)
        edges = [(rng.randrange(n),rng.randrange(n),rng.randrange(3),rng.randrange(6))
                 for _ in range(rng.randrange(7))]
        expected = brute_flow(n,edges,0,n-1)
        for dense in [False,True]:
            graph = MCFGraph(n,dense)
            for e in edges: graph.add_edge(*e)
            check_slope(graph.slope(0,n-1),expected)
        order = [n-1]+list(range(1,n-1))+[0]
        edges = []
        for _ in range(rng.randrange(7)):
            i,j = sorted(rng.sample(range(n),2))
            edges.append((order[i],order[j],rng.randrange(3),rng.randrange(-5,6)))
        expected = brute_flow(n,edges,n-1,0)
        for dense in [False,True]:
            graph = DAGMCFGraph(n,n-1,0,dense)
            for e in edges: graph.add_edge(*e)
            check_slope(graph.slope(),expected)
            graph = DAGMCFGraph(n,n-1,0,dense)
            for e in edges: graph.add_edge(*e)
            assert graph.min_cost() == min(expected.values())

    # SCC を全頂点対の到達可能性と比較する。
    for n in range(8):
        for _ in range(100):
            g = [[v for v in range(n) if rng.randrange(4) == 0] for u in range(n)]
            groups,comp,dag = find_SCC(g)
            reach = [[i==j or j in g[i] for j in range(n)] for i in range(n)]
            for k in range(n):
                for i in range(n):
                    for j in range(n): reach[i][j] |= reach[i][k] and reach[k][j]
            assert sorted(v for group in groups for v in group) == list(range(n))
            for i in range(n):
                for j in range(n):
                    assert (comp[i] == comp[j]) == (reach[i][j] and reach[j][i])
            assert all(c < d for c,adj in enumerate(dag) for d in adj)

    # 最大マッチングを全列挙し、平行辺も含めた辺・頂点の分類を確認する。
    for _ in range(300):
        nl,nr = rng.randrange(1,5),rng.randrange(1,5)
        edges = [(rng.randrange(nl),rng.randrange(nr)) for _ in range(rng.randrange(8))]
        graph = BipartiteMatching(nl,nr)
        for e in edges: graph.add_edge(*e)
        valid = []
        best = 0
        for bits in product([False,True],repeat=len(edges)):
            chosen = [e for e,b in zip(edges,bits) if b]
            if len({u for u,v in chosen}) != len(chosen) or len({v for u,v in chosen}) != len(chosen): continue
            if len(chosen) > best: best,valid = len(chosen),[]
            if len(chosen) == best: valid.append(bits)
        assert graph.solve() == best
        def status(flags):
            return ALWAYS if all(flags) else SOMETIMES if any(flags) else NEVER
        es,ls,rs = matching_structure(graph)
        assert es == [status([b[i] for b in valid]) for i in range(len(edges))]
        assert ls == [status([any(t and u==i for (u,v),t in zip(edges,b)) for b in valid]) for i in range(nl)]
        assert rs == [status([any(t and v==i for (u,v),t in zip(edges,b)) for b in valid]) for i in range(nr)]

    # トレイルの連続性、辺の完全被覆、連結成分ごとの次数による最小本数を比較する。
    for directed in [False,True]:
        cls = DirectedTrailDecomposition if directed else UndirectedTrailDecomposition
        for _ in range(1000):
            n = rng.randrange(1,8)
            edges = [(rng.randrange(n),rng.randrange(n)) for _ in range(rng.randrange(15))]
            dec = cls(n,edges)
            trails = dec.trail_decomposition()
            assert sorted(e for tr in trails for e in tr) == list(range(len(edges)))
            assert len(trails) == minimum_trails(n,edges,directed)
            for tr in trails:
                oriented = [edges[e] if directed else dec._orient[e] for e in tr]
                assert all(v == u for (_,v),(u,_) in zip(oriented,oriented[1:]))
