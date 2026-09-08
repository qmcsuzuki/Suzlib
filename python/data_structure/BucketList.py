# Ported from tatyam-prime/SortedSet:
# https://github.com/tatyam-prime/SortedSet/blob/main/BucketList.py
# Original repository license: The Unlicense
# https://github.com/tatyam-prime/SortedSet/blob/main/LICENSE

import math
from typing import Generic, Iterable, Iterator, TypeVar
T = TypeVar('T')

class BucketList(Generic[T]):
    """バケット分割で添字による取得・挿入・削除を行う可変長列。"""
    BUCKET_RATIO = 16
    SPLIT_RATIO = 24
    
    def __init__(self, a: Iterable[T] = []) -> None:
        """初期列をバケットに分割し、添字操作用の列を構築する。"""
        a = list(a)
        n = self.size = len(a)
        num_bucket = int(math.ceil(math.sqrt(n / self.BUCKET_RATIO)))
        self.a = [a[n * i // num_bucket : n * (i + 1) // num_bucket] for i in range(num_bucket)]

    def __iter__(self) -> Iterator[T]:
        """要素を順に列挙するイテレータを返す。"""
        for i in self.a:
            for j in i: yield j

    def __reversed__(self) -> Iterator[T]:
        """要素を逆順に列挙するイテレータを返す。"""
        for i in reversed(self.a):
            for j in reversed(i): yield j
    
    def __eq__(self, other) -> bool:
        """要素列が相手と等しいかを返す。"""
        if len(self) != len(other): return False
        for x, y in zip(self, other):
            if x != y: return False
        return True
    
    def __len__(self) -> int:
        """格納されている要素の個数を返す。"""
        return self.size
    
    def __repr__(self) -> str:
        """オブジェクトの内容を表すデバッグ用文字列を返す。"""
        return "BucketList" + str(self.a)
    
    def __str__(self) -> str:
        """現在の内容を表示用文字列に変換する。"""
        return str(list(self))

    def __contains__(self, x: T) -> bool:
        "Return True if x is in the bucket list. / O(N)"
        for y in self:
            if x == y: return True
        return False
    
    def _insert(self, a: list[T], b: int, i: int, x: T) -> None:
        """指定したバケット内に値を挿入し、大きすぎるバケットを分割する。"""
        a.insert(i, x)
        self.size += 1
        if len(a) > len(self.a) * self.SPLIT_RATIO:
            mid = len(a) >> 1
            self.a[b:b+1] = [a[:mid], a[mid:]]

    def insert(self, i: int, x: T) -> None:
        "Insert x at the i-th position. / O(√N)"
        if self.size == 0:
            if i != 0 and i != -1: raise IndexError
            self.a = [[x]]
            self.size = 1
            return
        if i < 0:
            for b, a in enumerate(reversed(self.a)):
                i += len(a)
                if i >= 0: return self._insert(a, len(self.a) + ~b, i, x)
        else:
            for b, a in enumerate(self.a):
                if i <= len(a): return self._insert(a, b, i, x)
                i -= len(a)
        raise IndexError

    def append(self, x: T) -> None:
        "Append x to the end of the list. / amortized O(1)"
        if self.size == 0:
            self.a = [[x]]
            self.size = 1
            return
        a = self.a[-1]
        return self._insert(a, len(self.a) - 1, len(a), x)
    
    def extend(self, a: Iterable[T]) -> None:
        """渡された要素列を末尾に追加する。"""
        for x in a: self.append(x)
    
    def __getitem__(self, i: int) -> T:
        """指定した添字またはキーに対応する値を返す。"""
        if i < 0:
            for a in reversed(self.a):
                i += len(a)
                if i >= 0: return a[i]
        else:
            for a in self.a:
                if i < len(a): return a[i]
                i -= len(a)
        raise IndexError
    
    def _pop(self, a: list[T], b: int, i: int) -> T:
        """指定したバケット内の要素を取り除いて返し、空のバケットを削除する。"""
        ans = a.pop(i)
        self.size -= 1
        if not a: del self.a[b]
        return ans
    
    def pop(self, i: int = -1) -> T:
        "Remove and return the i-th element. / O(√N) / O(-i) if i < 0"
        if i < 0:
            for b, a in enumerate(reversed(self.a)):
                i += len(a)
                if i >= 0: return self._pop(a, ~b, i)
        else:
            for b, a in enumerate(self.a):
                if i < len(a): return self._pop(a, b, i)
                i -= len(a)
        raise IndexError

    def count(self, x: T) -> int:
        "Return the number of occurrences of x. / O(N)"
        return sum(1 for y in self if x == y)

    def index(self, x: T) -> int:
        "Return the index of the first occurrence of x, raise ValueError if not found. / O(N)"
        for i, y in enumerate(self):
            if x == y: return i
        raise ValueError
    
    def remove(self, x: T) -> None:
        "Remove the first occurrence of x, raise ValueError if not found. / O(N)"
        self.pop(self.index(x))

    def clear(self) -> None:
        """すべての要素を削除する。"""
        self.a = []
        self.size = 0

    def reverse(self) -> None:
        """要素の並びを反転する。"""
        self.a.reverse()
        for a in self.a: a.reverse()

    def copy(self) -> 'BucketList[T]':
        """同じ要素を持つ浅いコピーを返す。"""
        return BucketList(self)
