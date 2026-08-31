# competitive-verifier: TITLE Hopcroft--Karp 法（一般の二部グラフ）

from python.graph.BipartiteMatching import (
    BipartiteMatching,
    GeneralBipartiteMatching,
)


class HopcroftKarp(GeneralBipartiteMatching):
    """GeneralBipartiteMatching の旧名。"""

    @classmethod
    def max_matching(
        cls, nL: int, nR: int, X2Y: list[list[int]]
    ) -> tuple[int, list[int], list[int]]:
        """左右に圧縮済みの隣接リストから最大マッチングを求める。"""
        matching = BipartiteMatching(nL, nR)
        matching.g = X2Y
        size = matching.solve()
        return size, matching.mate_left, matching.mate_right
