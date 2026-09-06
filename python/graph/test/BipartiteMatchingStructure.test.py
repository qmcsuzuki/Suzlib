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
    assert dm.groups == [dm.V0] + dm.blocks + [dm.Vinf]
    assert dm.s_comp == 0
    assert dm.t_comp == len(dm.groups) - 1
    assert len(dm.comp) == L + R
    assert len(dm.dag) == len(dm.groups)
    assert dm.state[dm.s_comp] == dm.SOURCE
    assert dm.state[dm.t_comp] == dm.SINK
    for v in dm.V0:
        assert dm.comp[v] == dm.s_comp
    for v in dm.Vinf:
        assert dm.comp[v] == dm.t_comp

    ans = matching.matching_edges()
    print(len(ans))
    for left, right in ans:
        print(left, right)


if __name__ == "__main__":
    main()
