# competitive-verifier: TITLE 削除可能ヒープ (Deletable Heapq)

from heapq import heapify, heappush, heappop
class DeletableHeapq:
    """
    削除可能heapq
    削除する元があることを仮定している（必要なときは別途 set や dict を持つ）
    """
    def __init__(self, initial = None):
        """初期列から最小ヒープを作り、遅延削除用の空のヒープを用意する。"""
        if initial is None:
            self.q = []
        else:
            self.q = list(initial)
            heapify(self.q)
        self.q_del = []

    def __len__(self):
        """格納されている要素の個数を返す。"""
        return len(self.q) - len(self.q_del)        
    
    def __str__(self):
        """現在の内容を表示用文字列に変換する。"""
        return f"queue:{self.q}" + "\n" + f"del:{self.q_del}"

    def propagate(self):
        """先頭に現れた削除予約済みの要素を二つのヒープから取り除く。"""
        while self.q_del and self.q[0] == self.q_del[0]:
            heappop(self.q)
            heappop(self.q_del)

    def heappop(self):
        """ヒープの先頭要素を取り除いて返す。"""
        self.propagate()
        return heappop(self.q)
    
    def top(self):
        """ヒープの先頭要素を削除せずに返す。"""
        self.propagate()
        return self.q[0]
            
    def remove(self,x):
        """存在する値 x を一つ遅延削除するため、削除用ヒープに登録する。"""
        heappush(self.q_del,x)

    def heappush(self,x):
        """値をヒープに追加する。"""
        heappush(self.q,x)

"""
要素が整数の場合、和も一緒に管理する特殊化
"""
class DeletableHeapqInt(DeletableHeapq):
    """任意要素の遅延削除と要素の総和を管理する整数最小ヒープ。"""
    def __init__(self, initial = None):
        """削除可能な整数最小ヒープを作り、初期要素の総和を求める。"""
        super().__init__(initial)
        self.sum = sum(self.q)

    def heappop(self):
        """ヒープの先頭要素を取り除いて返す。"""
        self.propagate()
        x = heappop(self.q)
        self.sum -= x
        return x

    def remove(self,x):
        """存在する値 x の遅延削除を予約し、管理する総和から差し引く。"""
        heappush(self.q_del,x)
        self.sum -= x

    def heappush(self,x):
        """値をヒープに追加する。"""
        heappush(self.q,x)
        self.sum += x
