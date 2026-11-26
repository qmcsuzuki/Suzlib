# competitive-verifier: TITLE 木の省メモリダブリング

class TreeDoubling:
    """根付き木の祖先取得、LCA、モノイド積。構築・メモリ O(N)、各クエリ O(log N)。
    usage:
        D = TreeDoubling(g, root=0)
        a = D.lca(u, v)
        D.set_weight(weights, op, e)  # weights[v]: v と親を結ぶ辺の重み
        w = D.path_weight(u, v)
    """
    def __init__(self, g, root=0):
        """連結な木の隣接リストから構築する。par[root] = -1。"""
        n = len(g)
        par = [-1] * n
        depth = [0] * n
        jump = [root] * n
        order = [root]
        for p in order:
            a = jump[p]
            b = jump[a]
            for v in g[p]:
                if v == par[p]:
                    continue
                par[v] = p
                depth[v] = depth[p] + 1
                jump[v] = b if depth[p] - depth[a] == depth[a] - depth[b] else p
                order.append(v)
        self.par, self.depth, self.jump = par, depth, jump
        self.order = order

    def kth_pos(self, k, v):
        """k 個上の祖先を返す (0 <= k <= depth[v])。"""
        par, depth, jump = self.par, self.depth, self.jump
        assert 0 <= k <= depth[v]
        d = depth[v] - k
        while depth[v] > d:
            u = jump[v]
            v = u if depth[u] >= d else par[v]
        return v

    def lca(self, u, v):
        """u と v の最近共通祖先を返す。"""
        par, depth, jump = self.par, self.depth, self.jump
        if depth[u] < depth[v]:
            u, v = v, u
        u = self.kth_pos(depth[u] - depth[v], u)
        while u != v:
            a, b = jump[u], jump[v]
            if a != b:
                u, v = a, b
            else:
                u, v = par[u], par[v]
        return u

    def distance(self, u, v):
        """u と v の間の辺数を返す。"""
        return self.depth[u] + self.depth[v] - 2 * self.depth[self.lca(u, v)]

    def set_weight(self, weights, op, e):
        """weights[v] は v と親の辺の重み (両方向共通、根の値は無視)。非可換可。"""
        par, jump = self.par, self.jump
        assert len(weights) == len(par)
        w = list(weights)
        w[self.order[0]] = e
        up, down = w[:], w[:]
        for v in self.order[1:]:
            p = par[v]
            if jump[v] != p:
                a = jump[p]
                up[v] = op(w[v], op(up[p], up[a]))
                down[v] = op(op(down[a], down[p]), w[v])
        self.w, self.up, self.down = w, up, down
        self.op, self.e = op, e

    def kth_weight_and_pos(self, k, v):
        """k 個上の祖先までの辺の積と祖先を (w, u) で返す。"""
        par, depth, jump = self.par, self.depth, self.jump
        assert 0 <= k <= depth[v]
        d = depth[v] - k
        w, op = self.e, self.op
        while depth[v] > d:
            u = jump[v]
            if depth[u] >= d:
                w, v = op(w, self.up[v]), u
            else:
                w, v = op(w, self.w[v]), par[v]
        return w, v

    def path_weight(self, u, v):
        """u から v への辺の積を順序通りに返す。空のパスは単位元。"""
        a = self.lca(u, v)
        par, depth, jump = self.par, self.depth, self.jump
        left, _ = self.kth_weight_and_pos(depth[u] - depth[a], u)
        right, op = self.e, self.op
        while v != a:
            b = jump[v]
            if depth[b] >= depth[a]:
                right, v = op(self.down[v], right), b
            else:
                right, v = op(self.w[v], right), par[v]
        return op(left, right)

    def binary_search(self, v, check):
        """FFF...TTT 型の check(w,u) が初めて真になる (k,w,u)。なければ (元の深さ+1, 根までの積, 根)。"""
        par, depth, jump = self.par, self.depth, self.jump
        k, w, op = 0, self.e, self.op
        while not check(w, v):
            if depth[v] == 0:
                return k + 1, w, v
            u = jump[v]
            nw = op(w, self.up[v])
            if not check(nw, u):
                k += depth[v] - depth[u]
                w, v = nw, u
            else:
                k += 1
                w, v = op(w, self.w[v]), par[v]
        return k, w, v
