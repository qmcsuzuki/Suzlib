# Ported from tatyam-prime/SortedSet:
# https://github.com/tatyam-prime/SortedSet/blob/main/SortedSet.py
# Original repository license: The Unlicense
# https://github.com/tatyam-prime/SortedSet/blob/main/LICENSE

import math
from bisect import bisect_left, bisect_right
from typing import Generic, Iterable, Iterator, TypeVar
T = TypeVar('T')

class SortedSet(Generic[T]):
    BUCKET_RATIO = 16
    SPLIT_RATIO = 24
    
    def __init__(self, a: Iterable[T] = []) -> None:
        "Make a new SortedSet from iterable. / O(N) if sorted and unique / O(N log N)"
        a = list(a)
        n = len(a)
        if any(a[i] > a[i + 1] for i in range(n - 1)):
            a.sort()
        if any(a[i] >= a[i + 1] for i in range(n - 1)):
            a, b = [], a
            for x in b:
                if not a or a[-1] != x:
                    a.append(x)
        n = self.size = len(a)
        num_bucket = int(math.ceil(math.sqrt(n / self.BUCKET_RATIO)))
        self.a = [a[n * i // num_bucket : n * (i + 1) // num_bucket] for i in range(num_bucket)]

    def __iter__(self) -> Iterator[T]:
        for i in self.a:
            for j in i: yield j

    def __reversed__(self) -> Iterator[T]:
        for i in reversed(self.a):
            for j in reversed(i): yield j
    
    def __eq__(self, other) -> bool:
        return list(self) == list(other)
    
    def __len__(self) -> int:
        return self.size
    
    def __repr__(self) -> str:
        return "SortedSet" + str(self.a)
    
    def __str__(self) -> str:
        s = str(list(self))
        return "{" + s[1 : len(s) - 1] + "}"

    def _position(self, x: T) -> tuple[list[T], int, int]:
        "return the bucket, index of the bucket and position in which x should be. self must not be empty."
        for i, a in enumerate(self.a):
            if x <= a[-1]: break
        return (a, i, bisect_left(a, x))

    def __contains__(self, x: T) -> bool:
        if self.size == 0: return False
        a, _, i = self._position(x)
        return i != len(a) and a[i] == x

    def add(self, x: T) -> bool:
        "Add an element and return True if added. / O(√N)"
        if self.size == 0:
            self.a = [[x]]
            self.size = 1
            return True
        a, b, i = self._position(x)
        if i != len(a) and a[i] == x: return False
        a.insert(i, x)
        self.size += 1
        if len(a) > len(self.a) * self.SPLIT_RATIO:
            mid = len(a) >> 1
            self.a[b:b+1] = [a[:mid], a[mid:]]
        return True
    
    def _pop(self, a: list[T], b: int, i: int) -> T:
        ans = a.pop(i)
        self.size -= 1
        if not a: del self.a[b]
        return ans

    def discard(self, x: T) -> bool:
        "Remove an element and return True if removed. / O(√N)"
        if self.size == 0: return False
        a, b, i = self._position(x)
        if i == len(a) or a[i] != x: return False
        self._pop(a, b, i)
        return True
    
    def lt(self, x: T) -> T | None:
        "Find the largest element < x, or None if it doesn't exist."
        for a in reversed(self.a):
            if a[0] < x:
                return a[bisect_left(a, x) - 1]

    def le(self, x: T) -> T | None:
        "Find the largest element <= x, or None if it doesn't exist."
        for a in reversed(self.a):
            if a[0] <= x:
                return a[bisect_right(a, x) - 1]

    def gt(self, x: T) -> T | None:
        "Find the smallest element > x, or None if it doesn't exist."
        for a in self.a:
            if a[-1] > x:
                return a[bisect_right(a, x)]

    def ge(self, x: T) -> T | None:
        "Find the smallest element >= x, or None if it doesn't exist."
        for a in self.a:
            if a[-1] >= x:
                return a[bisect_left(a, x)]
    
    def __getitem__(self, i: int) -> T:
        "Return the i-th element."
        if i < 0:
            for a in reversed(self.a):
                i += len(a)
                if i >= 0: return a[i]
        else:
            for a in self.a:
                if i < len(a): return a[i]
                i -= len(a)
        raise IndexError
    
    def pop(self, i: int = -1) -> T:
        "Pop and return the i-th element."
        if i < 0:
            for b, a in enumerate(reversed(self.a)):
                i += len(a)
                if i >= 0: return self._pop(a, ~b, i)
        else:
            for b, a in enumerate(self.a):
                if i < len(a): return self._pop(a, b, i)
                i -= len(a)
        raise IndexError
    
    def index(self, x: T) -> int:
        "Count the number of elements < x."
        ans = 0
        for a in self.a:
            if a[-1] >= x:
                return ans + bisect_left(a, x)
            ans += len(a)
        return ans

    def index_right(self, x: T) -> int:
        "Count the number of elements <= x."
        ans = 0
        for a in self.a:
            if a[-1] > x:
                return ans + bisect_right(a, x)
            ans += len(a)
        return ans

    def lower_bound_cursor(self, x: T) -> "SortedSetCursor[T]":
        """Return the boundary just before the first element >= x.
        Any modification to the set invalidates existing cursors.
        """
        for b, a in enumerate(self.a):
            if a[-1] >= x:
                return SortedSetCursor(self, b, bisect_left(a, x))
        return SortedSetCursor(self, len(self.a), 0)

    def upper_bound_cursor(self, x: T) -> "SortedSetCursor[T]":
        """Return the boundary just before the first element > x.
        Any modification to the set invalidates existing cursors.
        """
        for b, a in enumerate(self.a):
            if a[-1] > x:
                return SortedSetCursor(self, b, bisect_right(a, x))
        return SortedSetCursor(self, len(self.a), 0)

    def erase(self, first: "SortedSetCursor[T]", last: "SortedSetCursor[T]") -> int:
        """Erase [first, last) and return the number of erased elements.
        The cursors must belong to self and must not have been invalidated.
        """
        if first.s is not self or last.s is not self:
            raise ValueError("cursor belongs to another SortedSet")
        b1, i1 = first.b, first.i
        b2, i2 = last.b, last.i
        if (b1, i1) > (b2, i2):
            raise ValueError("invalid cursor range")
        if (b1, i1) == (b2, i2):
            return 0

        if b1 == b2:
            a = self.a[b1]
            n = i2 - i1
            del a[i1:i2]
            self.size -= n
            if not a:
                del self.a[b1]
            return n

        a = self.a
        left = a[b1]
        n = len(left) - i1
        del left[i1:]

        if b2 < len(a):
            right = a[b2]
            n += i2
            del right[:i2]
            for bucket in a[b1 + 1:b2]:
                n += len(bucket)
            keep = []
            if left:
                keep.append(left)
            if right:
                keep.append(right)
            a[b1:b2 + 1] = keep
        else:
            for bucket in a[b1 + 1:]:
                n += len(bucket)
            a[b1:] = [left] if left else []

        self.size -= n
        return n


class SortedSetCursor(Generic[T]):
    """A cursor at a boundary between two elements of a SortedSet."""

    __slots__ = ("s", "b", "i")

    def __init__(self, s: SortedSet[T], b: int, i: int) -> None:
        self.s = s
        self.b = b
        self.i = i

    def copy(self) -> "SortedSetCursor[T]":
        return SortedSetCursor(self.s, self.b, self.i)

    def prev(self) -> T | None:
        "Return the element immediately before the cursor without moving it."
        a = self.s.a
        if self.b == len(a):
            return a[-1][-1] if a else None
        if self.i:
            return a[self.b][self.i - 1]
        if self.b:
            return a[self.b - 1][-1]

    def next(self) -> T | None:
        "Return the element immediately after the cursor without moving it."
        if self.b == len(self.s.a):
            return None
        return self.s.a[self.b][self.i]

    def move_prev(self) -> bool:
        "Move one element to the left and return False if already at the beginning."
        a = self.s.a
        if not a or (self.b == 0 and self.i == 0):
            return False
        if self.b == len(a):
            self.b -= 1
            self.i = len(a[self.b]) - 1
        elif self.i:
            self.i -= 1
        else:
            self.b -= 1
            self.i = len(a[self.b]) - 1
        return True

    def move_next(self) -> bool:
        "Move one element to the right and return False if already at the end."
        a = self.s.a
        if self.b == len(a):
            return False
        self.i += 1
        if self.i == len(a[self.b]):
            self.b += 1
            self.i = 0
        return True
