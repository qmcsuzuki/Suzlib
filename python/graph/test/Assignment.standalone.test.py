# competitive-verifier: STANDALONE

from itertools import combinations, permutations
from random import Random

from python.graph.Assignment import assignment


def brute_force(cost: list[list[int]], flow: int) -> int:
    n = len(cost)
    m = len(cost[0]) if n else 0
    if flow == 0:
        return 0

    ans = None
    for lefts in combinations(range(n), flow):
        for rights in combinations(range(m), flow):
            for perm in permutations(rights):
                cur = sum(cost[i][j] for i, j in zip(lefts, perm))
                if ans is None or cur < ans:
                    ans = cur
    assert ans is not None
    return ans


def check(cost: list[list[int]], flow: int) -> None:
    min_cost, match = assignment(cost, flow)
    assert min_cost == brute_force(cost, flow)

    used = [j for j in match if j != -1]
    assert len(used) == flow
    assert len(set(used)) == flow
    assert min_cost == sum(cost[i][j] for i, j in enumerate(match) if j != -1)


if __name__ == "__main__":
    assert assignment([], 0) == (0, [])
    assert assignment([[], [], []], 0) == (0, [-1, -1, -1])

    rng = Random(0)
    for n in range(1, 5):
        for m in range(1, 5):
            for _ in range(30):
                cost = [
                    [rng.randrange(-10, 11) for _ in range(m)]
                    for _ in range(n)
                ]
                for flow in range(min(n, m) + 1):
                    check(cost, flow)

                min_cost, match = assignment(cost)
                flow = min(n, m)
                assert min_cost == brute_force(cost, flow)
                assert sum(j != -1 for j in match) == flow
