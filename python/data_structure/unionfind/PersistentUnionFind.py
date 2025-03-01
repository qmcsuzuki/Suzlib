from bisect import bisect_left
class PersistentUnionFind:
    """
    部分永続 unionfind
    初期時刻: clock = -1
    merge(x, y): clock を 1 進め、x と y を merge しようとする
    
    """
    MMM = 1<<30 #整数のペアを整数にエンコードするための数
    def __init__(self, n):
        self.parent_or_size = [-1]*n #非負: 親ノード, 負: サイズ
        self.merge_time = [self.MMM]*n # マージされた時刻
        self.time_size_history = [[1-self.MMM] for i in range(n)]
        self.clock = -1

    def leader(self, x, t=MMM-1): #leader(x): xの根ノードを返す．
        while self.merge_time[x] <= t:
            x = self.parent_or_size[x]
        return x 
 
    def merge(self, x, y): #merge(x,y): xのいる組とyのいる組をまとめる
        self.clock += 1 # まず時刻を進める
        x, y = self.leader(x), self.leader(y)
        if x == y: return -1
        if self.parent_or_size[x] > self.parent_or_size[y]: #xの要素数が大きいように
            x,y = y,x
        # yを x につなぐ
        self.merge_time[y] = self.clock
        self.parent_or_size[x] += self.parent_or_size[y]
        self.parent_or_size[y] = x
        self.time_size_history[x].append(self.clock*self.MMM - self.parent_or_size[x])
        return x
 
    def issame(self, x, y, t=MMM-1): #same(x,y): xとyが同じ組ならTrue
        return self.leader(x,t) == self.leader(y,t)
        
    def getsize(self,x, t=MMM-1): #size(x): xのいるグループの要素数を返す
        history = self.time_size_history[self.leader(x,t)]
        if t==self.MMM-1: return history[-1]%self.MMM
        idx = bisect_left(history,(t+1)*self.MMM)
        return history[idx-1]%self.MMM
    
    def get_merge_time(self,x,y):
        """
        x,y が連結になる最小時刻を求める（連結にならないなら self.MMM を返す）
        """
        t = -1
        while x != y:
            if self.merge_time[x] < self.merge_time[y]:
                t = self.merge_time[x]
                x = self.parent_or_size[x]
            else:
                t = self.merge_time[y]
                y = self.parent_or_size[y]
            if t == self.MMM: return self.MMM
        return t

    def binary_search(self, ng, ok, check):
        while ok-ng > 1:
            mid = (ok+ng)//2
            if check(mid):
                ok = mid
            else:
                ng = mid
        return ok

# https://atcoder.jp/contests/code-thanks-festival-2017/submissions/63313476
# https://atcoder.jp/contests/agc002/submissions/63313569
