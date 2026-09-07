# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/bipartitematching
# benchmark: sorted packed edges + linear scan grouping

from python.graph.BipartiteMatching import BipartiteMatching


class LinearBuildBipartiteMatching(BipartiteMatching):
    def _build_adjacency(self) -> None:
        if self._adj_built:
            return
        edges = sorted(self._edges)
        shift = self._edge_shift
        mask = self._edge_mask
        start = [0] * (self.n_left + 1)
        i = 0
        m = len(edges)
        for left in range(self.n_left):
            while i < m and edges[i] >> shift == left:
                i += 1
            start[left + 1] = i
        self.g = [
            [edge & mask for edge in edges[start[left]:start[left + 1]]]
            for left in range(self.n_left)
        ]
        self._adj_built = True


def main() -> None:
    L, R, M = map(int, input().split())
    matching = LinearBuildBipartiteMatching(L, R)
    for _ in range(M):
        a, b = map(int, input().split())
        matching.add_edge(a, b)

    print(matching.solve())
    for a, b in matching.matching_edges():
        print(a, b)


if __name__ == "__main__":
    main()
