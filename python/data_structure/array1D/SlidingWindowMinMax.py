# competitive-verifier: TITLE スライド最小値

"""
スライド最大値もあるよ！
スライド最小値、ただしあらかじめ配列を初期値として与える（参照渡しなので注意）
最小値が複数ある場合、q[0][0] は最も左の index
18 行目の > を >= に変えると最も右の index を返すようになる
"""

from collections import deque
class SlidingWindowMinimum:
    """両端が単調に進む区間の最小値を単調キューで求める。"""
    def __init__(self,a):
        """元の配列を参照し、最小値を追跡する空の単調キューを用意する。"""
        self.data = a
        self.R = 0
        self.q = deque() # (idx,val)

    # 半開区間 [l,r) の最小値を求める。
    # クエリの両端は広義単調増加
    def query(self,l,r):
        """両端が単調に進む非空の半開区間 [l,r) の最小値を返す。"""
        for i in range(self.R,r):
            while self.q and self.q[-1][1] > self.data[i]:
                self.q.pop()
            self.q.append((i,self.data[i]))
        while self.q[0][0] < l:
            self.q.popleft()
        self.R = r
        return self.q[0][1]

from collections import deque
class SlidingWindowMaximum:
    """両端が単調に進む区間の最大値を単調キューで求める。"""
    def __init__(self,a):
        """元の配列を参照し、最大値を追跡する空の単調キューを用意する。"""
        self.data = a
        self.R = 0
        self.q = deque() # (idx,val)

    # 半開区間 [l,r) の最大値を求める。
    # クエリの両端は広義単調増加
    def query(self,l,r):
        """両端が単調に進む非空の半開区間 [l,r) の最大値を返す。"""
        for i in range(self.R,r):
            while self.q and self.q[-1][1] < self.data[i]:
                self.q.pop()
            self.q.append((i,self.data[i]))
        while self.q[0][0] < l:
            self.q.popleft()
        self.R = r
        return self.q[0][1]
