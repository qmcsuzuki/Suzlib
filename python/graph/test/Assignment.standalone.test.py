# competitive-verifier: STANDALONE

from itertools import combinations, permutations
from random import Random

from python.graph.Assignment import assignment, assignment_costs


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

    costs = assignment_costs(cost, flow)
    assert len(costs) == flow + 1
    for f, value in enumerate(costs):
        assert value == brute_force(cost, f)


if __name__ == "__main__":
    assert assignment([], 0) == (0, [])
    assert assignment([[], [], []], 0) == (0, [-1, -1, -1])
    assert assignment_costs([], 0) == [0]
    assert assignment_costs([[], [], []], 0) == [0]

    rng = Random(0)
    for n in range(1, 5):
        for m in range(1, 5):
            for _ in range(30):
                cost = [
                    [rng.randrange(-10, 11) for _ in range(m)]
                    for _ in range(n)
                ]
                max_flow = min(n, m)
                for flow in range(max_flow + 1):
                    check(cost, flow)

                min_cost, match = assignment(cost)
                assert min_cost == brute_force(cost, max_flow)
                assert sum(j != -1 for j in match) == max_flow

                costs = assignment_costs(cost)
                assert costs == [brute_force(cost, f) for f in range(max_flow + 1)]
