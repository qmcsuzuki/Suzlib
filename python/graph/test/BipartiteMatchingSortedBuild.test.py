# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/bipartitematching

from bisect import bisect_left

from python.graph.BipartiteMatching import BipartiteMatching


class SortedBuildBipartiteMatching(BipartiteMatching):
    def __init__(self, n_left: int, n_right: int) -> None:
        super().__init__(n_left, n_right)
        self._adj_built = False

    def add_edge(self, left: int, right: int) -> int:
        assert 0 <= left < self.n_left
        assert 0 <= right < self.n_right
        edge_id = len(self._edges)
        self._edges.append((left << self._edge_shift) | right)
        self._solved = False
        return edge_id

    def solve(self) -> int:
        if not self._adj_built:
            edges = sorted(self._edges)
            shift = self._edge_shift
            mask = self._edge_mask
            start = [
                bisect_left(edges, left << shift)
                for left in range(self.n_left + 1)
            ]
            self.g = [
                [edge & mask for edge in edges[start[left]:start[left + 1]]]
                for left in range(self.n_left)
            ]
            self._adj_built = True
        return super().solve()


def main() -> None:
    L, R, M = map(int, input().split())
    matching = SortedBuildBipartiteMatching(L, R)
    for _ in range(M):
        a, b = map(int, input().split())
        matching.add_edge(a, b)

    print(matching.solve())
    for a, b in matching.matching_edges():
        print(a, b)


if __name__ == "__main__":
    main()
