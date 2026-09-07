# competitive-verifier: STANDALONE

from bisect import bisect_left
from random import Random
from time import perf_counter


def bisect_boundaries(edges: list[int], n_left: int, shift: int) -> list[int]:
    return [bisect_left(edges, left << shift) for left in range(n_left + 1)]


def threshold_boundaries(edges: list[int], n_left: int, shift: int) -> list[int]:
    start = [0] * (n_left + 1)
    i = 0
    m = len(edges)
    for left in range(n_left):
        threshold = (left + 1) << shift
        while i < m and edges[i] < threshold:
            i += 1
        start[left + 1] = i
    return start


def main() -> None:
    n_left = 100_000
    n_right = 100_000
    m = 200_000
    shift = max(1, (n_right - 1).bit_length())
    rng = Random(0)
    edges = sorted((rng.randrange(n_left) << shift) | rng.randrange(n_right) for _ in range(m))

    a = bisect_boundaries(edges, n_left, shift)
    b = threshold_boundaries(edges, n_left, shift)
    assert a == b

    # JIT warm-up
    for _ in range(3):
        bisect_boundaries(edges, n_left, shift)
        threshold_boundaries(edges, n_left, shift)

    tb = 0.0
    tt = 0.0
    for rep in range(10):
        if rep & 1:
            t = perf_counter()
            threshold_boundaries(edges, n_left, shift)
            tt += perf_counter() - t
            t = perf_counter()
            bisect_boundaries(edges, n_left, shift)
            tb += perf_counter() - t
        else:
            t = perf_counter()
            bisect_boundaries(edges, n_left, shift)
            tb += perf_counter() - t
            t = perf_counter()
            threshold_boundaries(edges, n_left, shift)
            tt += perf_counter() - t

    print(f"bisect={tb:.6f} threshold={tt:.6f} ratio={tt / tb:.4f}")


if __name__ == "__main__":
    main()
