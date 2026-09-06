# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/bipartitematching

from python.graph.BipartiteMatching import BipartiteMatching
from python.graph.DulmageMendelsohn import DulmageMendelsohn
from python.graph.MatchingStructure import MatchingStructure


def main() -> None:
    L, R, M = map(int, input().split())
    matching = BipartiteMatching(L, R)
    for _ in range(M):
        left, right = map(int, input().split())
        matching.add_edge(left, right)

    matching.solve()

    structure = MatchingStructure(matching)
    assert len(structure.edge_status) == M
    for edge_id in matching.matching_edge_ids():
        assert structure.edge_status[edge_id] != structure.NEVER

    dm = DulmageMendelsohn(matching)
    assert dm.state[dm.s_comp] == dm.SOURCE
    assert dm.state[dm.t_comp] == dm.SINK

    ans = matching.matching_edges()
    print(len(ans))
    for left, right in ans:
        print(left, right)


if __name__ == "__main__":
    main()
