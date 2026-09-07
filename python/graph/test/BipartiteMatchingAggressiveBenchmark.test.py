# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/aplusb

from random import seed
from time import perf_counter

from python.graph.BipartiteMatching import BipartiteMatching
from python.graph.BipartiteMatchingAggressive import (
    BipartiteMatchingAggressive,
    BipartiteMatchingAggressiveRaw,
)


def kuhn_killer(n=100000):
    k = n // 8 * 2
    edges = []
    for i in range(k):
        edges.append((i, i))
    for i in range(k - 1):
        edges.append((i + 1, i))
    for i in range(k // 2):
        edges.append((i, k + 2 * i))
        edges.append((2 * k + 2 * i, k + 2 * i))
        edges.append((2 * k + 2 * i, 3 * k + 2 * i))
        edges.append((k + 2 * i, i))
        edges.append((k + 2 * i, 2 * k + 2 * i))
        edges.append((3 * k + 2 * i, 2 * k + 2 * i))
    for j in range(k // 2):
        i = k // 2 - 1 - j
        edges.append((k // 2 + j, k + 2 * i + 1))
        edges.append((2 * k + 2 * i + 1, k + 2 * i + 1))
        edges.append((2 * k + 2 * i + 1, 3 * k + 2 * i + 1))
        edges.append((k + 2 * i + 1, k // 2 + j))
        edges.append((k + 2 * i + 1, 2 * k + 2 * i + 1))
        edges.append((3 * k + 2 * i + 1, 2 * k + 2 * i + 1))
    return edges


def build(cls, n, edges):
    matching = cls(n, n)
    for a, b in edges:
        matching.add_edge(a, b)
    return matching


def timed(cls, n, edges):
    matching = build(cls, n, edges)
    seed(123456789)
    t0 = perf_counter()
    size = matching.solve()
    return perf_counter() - t0, size


def main():
    a, b = map(int, input().split())
    n = 100000
    edges = kuhn_killer(n)
    classes = [
        ("current", BipartiteMatching),
        ("aggressive", BipartiteMatchingAggressive),
        ("aggressive_raw", BipartiteMatchingAggressiveRaw),
    ]

    # warm up PyPy JIT on a smaller graph
    warm_edges = kuhn_killer(8000)
    for _, cls in classes:
        timed(cls, 8000, warm_edges)

    expected = None
    for rep in range(3):
        order = classes if rep % 2 == 0 else classes[::-1]
        for name, cls in order:
            t, size = timed(cls, n, edges)
            if expected is None:
                expected = size
            assert size == expected
            print(f"BENCH rep={rep} impl={name} time={t:.6f} size={size}")

    print(a + b)


if __name__ == "__main__":
    main()
