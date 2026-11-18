# competitive-verifier: TITLE DAG の最大重み反鎖

from python.graph.flow.maxflow.DAGMinimumPathCover import DAGMinimumPathCover


class DAGMaximumAntichain(DAGMinimumPathCover):
    """最大重み反鎖用の互換クラス。頂点共有を許す最小パス被覆として解く。"""

    def __init__(self, n: int, weights: list[int] | None = None) -> None:
        super().__init__(n, disjoint=False)
        if weights is not None:
            assert len(weights) == n and all(isinstance(w, int) and w >= 0 for w in weights)
            self._weights = list(weights)
