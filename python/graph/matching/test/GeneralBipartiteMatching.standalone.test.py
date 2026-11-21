# competitive-verifier: STANDALONE

from itertools import product
from random import Random

from python.graph.matching.BipartiteMatching import BipartiteMatching
from python.graph.matching.BipartiteMatchingStructure import ALWAYS, NEVER, SOMETIMES, DulmageMendelsohn
from python.graph.matching.GeneralBipartiteMatching import GeneralBipartiteMatching
from python.graph.matching.GeneralBipartiteMatchingStructure import GeneralDulmageMendelsohn, general_matching_structure


def rejects(fn, error=ValueError):
    try:
        fn()
    except error:
        return
    raise AssertionError('expected exception')


def rebuild(n_left, n_right, edges):
    matching = BipartiteMatching(n_left, n_right)
    for edge in edges:
        matching.add_edge(*edge)
    return matching.solve()


def status(flags):
    return ALWAYS if all(flags) else SOMETIMES if any(flags) else NEVER


def check(rng, nl, nr):
    """左右に分かれたランダムな二部グラフを一つの番号空間に埋め込み、全列挙と比較する。"""
    edges = [(rng.randrange(nl), rng.randrange(nr)) for _ in range(rng.randrange(8) if nl and nr else 0)]
    # 最大マッチングを全列挙する（AlgorithmAudit と同じ方法）。
    valid = []
    best = 0
    for bits in product([False, True], repeat=len(edges)):
        chosen = [e for e, b in zip(edges, bits) if b]
        if len({u for u, v in chosen}) != len(chosen) or len({v for u, v in chosen}) != len(chosen):
            continue
        if len(chosen) > best:
            best, valid = len(chosen), []
        if len(chosen) == best:
            valid.append(bits)

    n = nl + nr + rng.randrange(3)  # 孤立頂点も混ぜる
    label = list(range(n))
    rng.shuffle(label)
    left, right = label[:nl], label[nl:nl + nr]
    general_edges = []
    for u, v in edges:
        e = (left[u], right[v])
        general_edges.append(e if rng.randrange(2) else e[::-1])

    g = GeneralBipartiteMatching(n)
    for i, (u, v) in enumerate(general_edges):
        assert g.add_edge(u, v) == i
    assert g.solve() == best

    pairs = {frozenset(e) for e in general_edges}
    matched = g.matching_edges()
    assert len(matched) == best
    assert len({x for e in matched for x in e}) == 2 * best
    assert all(frozenset(e) in pairs and g.color[e[0]] == 0 and g.color[e[1]] == 1 for e in matched)

    ids = g.matching_edge_ids()
    assert len(ids) == len(set(ids)) == best
    assert {frozenset(general_edges[i]) for i in ids} == {frozenset(e) for e in matched}

    mate = g.mates()
    assert sum(m != -1 for m in mate) == 2 * best
    assert all(mate[u] == v and mate[v] == u for u, v in matched)

    cover = g.min_vertex_cover()
    assert len(cover) == best and all(u in cover or v in cover for u, v in general_edges)
    independent = set(g.max_independent_set())
    assert len(independent) == n - best
    assert not any(u in independent and v in independent for u, v in general_edges)

    edge_status, vertex_status = general_matching_structure(g)
    assert edge_status == [status([b[i] for b in valid]) for i in range(len(edges))]
    expected = [NEVER] * n
    for i in range(nl):
        expected[left[i]] = status([any(t and u == i for (u, v), t in zip(edges, b)) for b in valid])
    for i in range(nr):
        expected[right[i]] = status([any(t and v == i for (u, v), t in zip(edges, b)) for b in valid])
    assert vertex_status == expected

    # solve 後の add_edge は彩色から作り直す。
    if nl and nr:
        u, v = rng.randrange(nl), rng.randrange(nr)
        g.add_edge(right[v], left[u])
        assert g.solve() == rebuild(nl, nr, edges + [(u, v)])


def check_dm(rng, nl, nr):
    """右 j を j、左 i を nr+i と番号付けし、各左頂点に辺を持たせると、自動彩色は
    左を色 0、右を色 1 にする。このとき元の DulmageMendelsohn と一致することを確認する。"""
    edges = [(i, rng.randrange(nr)) for i in range(nl)]
    edges += [(rng.randrange(nl), rng.randrange(nr)) for _ in range(rng.randrange(8))]
    matching = BipartiteMatching(nl, nr)
    g = GeneralBipartiteMatching(nl + nr)
    for u, v in edges:
        matching.add_edge(u, v)
        g.add_edge(nr + u, v)
    dm = DulmageMendelsohn(matching)
    gdm = GeneralDulmageMendelsohn(g)
    label = lambda x: nr + x if x < nl else x - nl  # DM の統合番号 → 一般版の番号

    assert gdm.color == [1] * nr + [0] * nl
    assert sorted(gdm.V0) == sorted(map(label, dm.V0))
    assert sorted(gdm.Vinf) == sorted(map(label, dm.Vinf))
    as_set = lambda groups: {frozenset(group) for group in groups}
    assert as_set(gdm.blocks) == {frozenset(map(label, b)) for b in dm.blocks}
    assert len(gdm.groups) == len(gdm.blocks) + 2
    for k, group in enumerate(gdm.groups):
        assert all(gdm.groupnum[v] == k for v in group)
    assert sorted(v for group in gdm.groups for v in group) == list(range(nl + nr))
    assert all(a < b for a, adj in enumerate(gdm.dag) for b in adj)


rng = Random(0)
for nl in range(5):
    for nr in range(5):
        for _ in range(30):
            check(rng, nl, nr)
for nl in range(1, 6):
    for nr in range(1, 6):
        for _ in range(30):
            check_dm(rng, nl, nr)

# 二部グラフでなければ ValueError。
for n, edges in [(1, [(0, 0)]), (3, [(0, 1), (1, 2), (2, 0)]),
                 (7, [(0, 1), (2, 3), (3, 4), (4, 5), (5, 6), (6, 2)])]:
    g = GeneralBipartiteMatching(n)
    for e in edges:
        g.add_edge(*e)
    rejects(g.solve)

g = GeneralBipartiteMatching(0)
assert g.solve() == 0 and g.matching_edges() == [] and g.mates() == []
print('GeneralBipartiteMatching tests passed')
