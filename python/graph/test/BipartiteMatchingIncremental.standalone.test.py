# competitive-verifier: STANDALONE

from random import Random

from python.graph.BipartiteMatching import BipartiteMatching


def rebuild(n_left: int, n_right: int, edges: list[tuple[int, int] | None]) -> int:
    matching = BipartiteMatching(n_left, n_right)
    for edge in edges:
        if edge is not None:
            matching.add_edge(*edge)
    return matching.solve()


def check(matching: BipartiteMatching, edges: list[tuple[int, int] | None]) -> None:
    assert matching.size == rebuild(matching.n_left, matching.n_right, edges)

    active = {edge for edge in edges if edge is not None}
    used_left = set()
    used_right = set()
    for left, right in matching.matching_edges():
        assert (left, right) in active
        assert left not in used_left
        assert right not in used_right
        used_left.add(left)
        used_right.add(right)
    assert len(used_left) == matching.size


def test_increment_edge(rng: Random, n_left: int, n_right: int) -> None:
    matching = BipartiteMatching(n_left, n_right)
    matching.solve()
    edges: list[tuple[int, int] | None] = []

    candidates = [(left, right) for left in range(n_left) for right in range(n_right)]
    rng.shuffle(candidates)
    for left, right in candidates:
        old_size = matching.size
        grew = matching.increment_edge(left, right)
        edges.append((left, right))
        check(matching, edges)
        assert grew == (matching.size > old_size)


def test_increment_edges_from_left(rng: Random, n_left: int, n_right: int) -> None:
    matching = BipartiteMatching(n_left, n_right)
    matching.solve()
    edges: list[tuple[int, int] | None] = []

    order = list(range(n_left))
    rng.shuffle(order)
    for left in order:
        rights = list(range(n_right))
        rng.shuffle(rights)
        rights = rights[: rng.randrange(n_right + 1)]
        old_size = matching.size
        grew = matching.increment_edges_from_left(left, rights)
        edges.extend((left, right) for right in rights)
        check(matching, edges)
        assert grew == (matching.size > old_size)


def test_increment_edges_from_right(rng: Random, n_left: int, n_right: int) -> None:
    matching = BipartiteMatching(n_left, n_right)
    matching.solve()
    edges: list[tuple[int, int] | None] = []

    order = list(range(n_right))
    rng.shuffle(order)
    for right in order:
        lefts = list(range(n_left))
        rng.shuffle(lefts)
        lefts = lefts[: rng.randrange(n_left + 1)]
        old_size = matching.size
        grew = matching.increment_edges_from_right(right, lefts)
        edges.extend((left, right) for left in lefts)
        check(matching, edges)
        assert grew == (matching.size > old_size)


def test_remove_edge(rng: Random, n_left: int, n_right: int) -> None:
    matching = BipartiteMatching(n_left, n_right)
    candidates = [(left, right) for left in range(n_left) for right in range(n_right)]
    rng.shuffle(candidates)
    candidates = candidates[: rng.randrange(len(candidates) + 1)]

    edges: list[tuple[int, int] | None] = []
    edge_ids = []
    for left, right in candidates:
        edge_ids.append(matching.add_edge(left, right))
        edges.append((left, right))
    matching.solve()
    check(matching, edges)

    rng.shuffle(edge_ids)
    for edge_id in edge_ids:
        old_size = matching.size
        decreased = matching.remove_edge(edge_id)
        edges[edge_id] = None
        check(matching, edges)
        assert decreased == (matching.size < old_size)


if __name__ == "__main__":
    rng = Random(0)
    for n_left in range(1, 8):
        for n_right in range(1, 8):
            for _ in range(10):
                test_increment_edge(rng, n_left, n_right)
                test_increment_edges_from_left(rng, n_left, n_right)
                test_increment_edges_from_right(rng, n_left, n_right)
                test_remove_edge(rng, n_left, n_right)
