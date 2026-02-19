# competitive-verifier: TITLE 最大二部マッチング（辺追加可能）
# https://judge.yosupo.jp/submission/353978

from collections import deque
import random

class DynamicBipartiteMatching:
    """
    動的（頂点追加・辺追加）対応の二部最大マッチング（増分更新）
    アルゴリズム: 多始点BFS + Kuhn (増大路がある限り増やす)
    """
    def __init__(self, n: int, m: int):
        self.n = n
        self.m = m
        self.g: list[list[int]] = [[] for _ in range(n)]

        self.X2Y: list[int] = [-1] * n
        self.Y2X: list[int] = [-1] * m
        self.cnt = 0

        self._built = False

    def add_edge(self, x: int, y: int) -> None:
        """build() 前専用: 辺を追加するだけ（マッチングは更新しない）。"""
        if self._built:
            raise RuntimeError("add_edge() is allowed only before build(). Use increment_edge() after build().")
        self.g[x].append(y)

    def max_matching(self) -> tuple[int, list[int], list[int]]:
        """現在のグラフで最大マッチングを構築し、(サイズ, X2Y, Y2X) を返す。"""
        if self._built:
            return self.cnt, self.X2Y, self.Y2X
        self._built = True
        self._greedy_init() # 最初だけランダム貪欲マッチング
        while self._augment_from_all_free_left():
            pass
        return self.cnt, self.X2Y, self.Y2X

    def _greedy_init(self) -> None:
        """
        左頂点をランダム順に見て、空いている右頂点があれば即マッチ。
        （最初の1回だけ。最大性は後段の増大路探索で保証される）
        """
        g = self.g
        X2Y = self.X2Y
        Y2X = self.Y2X

        order = list(range(self.n))
        random.shuffle(order)
        for lst in g:
            random.shuffle(order)


        for x in order:
            if X2Y[x] != -1:
                continue
            for y in g[x]:
                if Y2X[y] == -1:
                    X2Y[x] = y
                    Y2X[y] = x
                    self.cnt += 1
                    break

    def increment_edge(self, x: int, y: int) -> bool:
        """max_matching() 後: 辺 (x,y) を追加し、増分更新（高々1）を1回だけ試す。"""
        assert self._built
        self.g[x].append(y)

        if self.X2Y[x] == -1 and self.Y2X[y] == -1:
            self.X2Y[x] = y
            self.Y2X[y] = x
            self.cnt += 1
            return True

        return self._augment_from_all_free_left()

    def increment_edges_from_left(self, x: int, right_vertices: list[int]) -> bool:
        """max_matching() 後: 左 x から複数の右頂点へ辺追加し、増分更新を1回だけ試す。"""
        assert self._built
        self.g[x].extend(right_vertices)

        if self.X2Y[x] == -1:
            for y in right_vertices:  # FIX: edges -> right_vertices
                if self.Y2X[y] == -1:
                    self.X2Y[x] = y
                    self.Y2X[y] = x
                    self.cnt += 1
                    return True

        return self._augment_from_all_free_left()

    def increment_edges_from_right(self, y: int, left_vertices: list[int]) -> bool:
        """max_matching() 後: 右 y に対し、複数の左頂点から y への辺を追加し、増分更新を1回だけ試す。"""
        assert self._built
        for x in left_vertices:
            self.g[x].append(y)

        if self.Y2X[y] == -1:
            for x in left_vertices:   # FIX: edges -> left_vertices
                if self.X2Y[x] == -1:
                    self.X2Y[x] = y
                    self.Y2X[y] = x
                    self.cnt += 1
                    return True
        
        return self._augment_from_all_free_left()

    def _augment_from_all_free_left(self) -> bool:
        """
        多始点BFS を 1 回走らせ、その最中に見つかる限り増大路を反転する。
        戻り値: そのラウンドで 1 回でも更新したか
        """
        g = self.g
        X2Y = self.X2Y
        Y2X = self.Y2X

        q = deque()
        root = [-1] * self.n
        par = [-1] * self.n

        for i in range(self.n):
            if X2Y[i] == -1:
                q.append(i)
                root[i] = i

        updated = False

        while q:
            x = q.popleft()
            if X2Y[root[x]] != -1:
                continue

            for y in g[x]:
                if Y2X[y] == -1:
                    while y != -1:
                        Y2X[y] = x
                        y, X2Y[x] = X2Y[x], y
                        x = par[x]
                    self.cnt += 1
                    updated = True
                    break

                nx = Y2X[y]
                if root[nx] != -1:
                    continue
                par[nx] = x
                root[nx] = root[x]
                q.append(nx)

        return updated
