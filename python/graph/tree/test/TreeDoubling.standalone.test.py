# competitive-verifier: STANDALONE

from random import Random
from python.graph.tree.TreeDoubling import TreeDoubling


if __name__ == "__main__":
    rng = Random(20261126)
    for n in [1, 2, 3, 7, 15, 31, 64, 127, 256]:
        for shape in range(8):
            g = [[] for _ in range(n)]
            for v in range(1, n):
                p = v-1 if shape == 0 else 0 if shape == 1 else rng.randrange(v)
                g[p].append(v)
                g[v].append(p)
            root = rng.randrange(n)
            D = TreeDoubling(g, root)
            assert not hasattr(D, "up")
            # Independent paths from a traversal starting at the root.
            paths = [[] for _ in range(n)]
            paths[root] = [root]
            stack = [root]
            while stack:
                v = stack.pop()
                for u in g[v]:
                    if not paths[u]:
                        paths[u] = [u] + paths[v]
                        stack.append(u)
            D.set_weight([(v,) for v in range(n)], tuple.__add__, ())
            for _ in range(300):
                u, v = rng.randrange(n), rng.randrange(n)
                p, q = paths[u], paths[v]
                a = next(x for x in p if x in q)
                i, j = p.index(a), q.index(a)
                assert D.lca(u, v) == a
                assert D.distance(u, v) == i+j
                k = rng.randrange(len(p))
                assert D.kth_pos(k, u) == p[k]
                assert D.kth_weight_and_pos(k, u) == (tuple(p[:k]), p[k])
                assert D.path_weight(u, v) == tuple(p[:i] + q[:j][::-1])
                t = rng.randrange(len(p)+1)
                m = min(t, len(p)-1)
                assert D.binary_search(u, lambda w, v: len(w) >= t) == (t, tuple(p[:m]), p[m])
            # Reinitializing the weights must not alter the jump structure.
            D.set_weight([1]*n, int.__add__, 0)
            for v in range(n):
                assert D.kth_weight_and_pos(D.depth[v], v) == (len(paths[v])-1, root)
