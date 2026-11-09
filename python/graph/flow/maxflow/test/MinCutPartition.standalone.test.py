# competitive-verifier: STANDALONE
from random import Random

from python.graph.flow.maxflow.MaxFlow import MFGraph


def check(n, edges, s, t):
    g = MFGraph(n)
    for u, v, c in edges:
        g.add_edge(u, v, c)
    value = g.flow(s, t)
    before = g.edges()
    group = g.min_cut_partition(s, t)
    assert g.edges() == before
    assert g.min_cut_partition(s, t) == group
    # 全ての最小カットを列挙。常にs側なら0、常にt側なら2、それ以外は1。
    cuts = []
    for mask in range(1 << n):
        if not (mask >> s & 1) or mask >> t & 1:
            continue
        cost = sum(c for u, v, c in edges if mask >> u & 1 and not (mask >> v & 1))
        if cost == value:
            cuts.append(mask)
    assert cuts
    expected = [0 if all(mask >> v & 1 for mask in cuts) else
                2 if all(not (mask >> v & 1) for mask in cuts) else 1
                for v in range(n)]
    assert group == expected, (edges, group, expected)


check(3, [], 0, 2)
check(5, [(0, 1, 2), (1, 2, 1), (2, 4, 2)], 0, 4)
check(4, [(0, 1, 1), (1, 2, 1), (2, 3, 1)], 0, 3)
rng = Random(413)
for _ in range(400):
    n = rng.randrange(2, 8)
    s, t = rng.sample(range(n), 2)
    edges = [(rng.randrange(n), rng.randrange(n), rng.randrange(4))
             for _ in range(rng.randrange(25))]
    check(n, edges, s, t)

g = MFGraph(2)
g.add_edge(0, 1, 2)
g.flow(0, 1, 1)
try:
    g.min_cut_partition(0, 1)
except AssertionError:
    pass
else:
    raise AssertionError('unfinished max flow accepted')
g.flow(0, 1)
assert g.min_cut_partition(0, 1) == [0, 2]
print('MinCutPartition tests passed')
