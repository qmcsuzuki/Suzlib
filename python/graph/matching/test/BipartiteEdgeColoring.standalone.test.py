# competitive-verifier: STANDALONE

from random import Random

from python.graph.matching.BipartiteEdgeColoring import BipartiteEdgeColoring


def check(n_left, n_right, edges):
    g = BipartiteEdgeColoring(n_left, n_right)
    for i, (u, v) in enumerate(edges):
        assert g.add_edge(u, v) == i
    degree = [0] * (n_left + n_right)
    for u, v in edges:
        degree[u] += 1
        degree[n_left + v] += 1
    delta = max(degree, default=0)
    assert g.solve() == delta
    assert g.solve() == delta
    colors = g.edge_colors()
    classes = g.color_classes()
    assert len(colors) == len(edges) and len(classes) == delta
    assert sorted(e for cls in classes for e in cls) == list(range(len(edges)))
    seen = set()
    for eid, (u, v) in enumerate(edges):
        color = colors[eid]
        assert 0 <= color < delta
        assert eid in classes[color]
        assert (0, u, color) not in seen
        assert (1, v, color) not in seen
        seen.add((0, u, color))
        seen.add((1, v, color))
    for c in range(delta):
        assert classes[c]
    if colors:
        old = colors[0]
        colors[0] = -1
        assert g.edge_colors()[0] == old
    classes.append([])
    assert len(g.color_classes()) == delta
    if delta == 0:
        assert colors == []


def test_api():
    g = BipartiteEdgeColoring(2, 2)
    for method in (g.edge_colors, g.color_classes):
        try:
            method()
        except RuntimeError:
            pass
        else:
            assert False
    assert g.solve() == 0
    try:
        g.add_edge(0, 0)
    except RuntimeError:
        pass
    else:
        assert False


def test_random():
    rng = Random(0)
    for n_left in range(0, 7):
        for n_right in range(0, 7):
            for _ in range(250):
                edges = [
                    (rng.randrange(n_left), rng.randrange(n_right))
                    for _ in range(rng.randrange(18) if n_left and n_right else 0)
                ]
                check(n_left, n_right, edges)


def test_unbalanced():
    check(1, 100, [(0, v) for v in range(100)])
    check(100, 1, [(v, 0) for v in range(100)])
    check(200, 200, [(0, 0)] * 100 + [(v, v) for v in range(1, 200)])


def test_regular():
    rng = Random(2)
    for n in range(1, 20):
        for k in range(1, 25):
            edges = []
            for _ in range(k):
                p = list(range(n))
                rng.shuffle(p)
                edges.extend((i, p[i]) for i in range(n))
            rng.shuffle(edges)
            check(n, n, edges)


if __name__ == "__main__":
    test_api()
    test_random()
    test_unbalanced()
    test_regular()
