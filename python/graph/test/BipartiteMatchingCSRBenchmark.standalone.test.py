# competitive-verifier: STANDALONE

from random import Random, seed
from time import perf_counter

from python.graph.BipartiteMatching import BipartiteMatching
from python.graph.BipartiteMatchingCSR import BipartiteMatchingCSR


def build(cls, n, edges):
    matching = cls(n, n)
    for left, right in edges:
        matching.add_edge(left, right)
    return matching


def measure(cls, n, edges, random_seed):
    matching = build(cls, n, edges)
    seed(random_seed)
    t0 = perf_counter()
    size = matching.solve()
    return perf_counter() - t0, size


def main():
    n = 100_000
    m = 200_000
    rng = Random(123456789)
    edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(m)]

    # PyPy JIT warm-up.
    warm_edges = edges[:20_000]
    measure(BipartiteMatching, 10_000, [(a % 10_000, b % 10_000) for a, b in warm_edges], 0)
    measure(BipartiteMatchingCSR, 10_000, [(a % 10_000, b % 10_000) for a, b in warm_edges], 0)

    baseline_times = []
    csr_times = []
    for rep in range(4):
        order = (BipartiteMatching, BipartiteMatchingCSR) if rep % 2 == 0 else (BipartiteMatchingCSR, BipartiteMatching)
        result = {}
        for cls in order:
            t, size = measure(cls, n, edges, 1000 + rep)
            result[cls] = (t, size)
        baseline_t, baseline_size = result[BipartiteMatching]
        csr_t, csr_size = result[BipartiteMatchingCSR]
        assert baseline_size == csr_size
        baseline_times.append(baseline_t)
        csr_times.append(csr_t)
        print(f"rep={rep} baseline={baseline_t:.6f} csr={csr_t:.6f} ratio={csr_t / baseline_t:.4f} size={baseline_size}")

    baseline_avg = sum(baseline_times) / len(baseline_times)
    csr_avg = sum(csr_times) / len(csr_times)
    print(f"avg baseline={baseline_avg:.6f} csr={csr_avg:.6f} ratio={csr_avg / baseline_avg:.4f}")


if __name__ == "__main__":
    main()
