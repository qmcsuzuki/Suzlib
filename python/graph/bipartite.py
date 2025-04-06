# verification-helper: TITLE 二部グラフ判定

class bipartite(UnionFind):
    def __init__(self, n):
        super().__init__(2*n)
        self.n = n
        self.is_bipartite = True

    def add_edge(self,u,v):
        self.merge(u,v+self.n)
        self.merge(u+self.n,v)
        if self.issame(u,u+self.n):
            self.is_bipartite = False

    def add_same(self,u,v):
        self.merge(u,v)
        self.merge(u+self.n,v+self.n)
        if self.issame(u,u+self.n):
            self.is_bipartite = False

    def all_connected_components(self):
        res = []
        used = [0]*self.n
        for lst in self.groups():
            v = lst[0]%self.n
            if used[v]: continue
            x = y = 0
            for v in lst:
                if v < self.n:
                    x += 1
                else:
                    y += 1
                    v -= self.n
                used[v] = 1
            res.append((x,y))
        return res

    def number_of_connected_component(self):
        return self.num_conn_comp//2
