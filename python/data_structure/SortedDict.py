# SortedDict using the same square-root-decomposition design as tatyam-prime/SortedSet:
# https://github.com/tatyam-prime/SortedSet/blob/main/SortedSet.py
# The referenced implementation is released under The Unlicense:
# https://github.com/tatyam-prime/SortedSet/blob/main/LICENSE
#
# Note: tatyam-prime/SortedSet does not provide a SortedDict implementation.
# This file is a Suzlib implementation built on the same bucketed sorted-key design.

import math
from bisect import bisect_left, bisect_right
from typing import Generic, Iterable, Iterator, Mapping, TypeVar
K = TypeVar('K')
V = TypeVar('V')


class SortedDict(Generic[K, V]):
    BUCKET_RATIO = 16
    SPLIT_RATIO = 24

    def __init__(self, a: Mapping[K, V] | Iterable[tuple[K, V]] = ()) -> None:
        if hasattr(a, "items"):
            d = dict(a.items())
        else:
            d = dict(a)
        keys = list(d)
        keys.sort()
        self.d = d
        n = self.size = len(keys)
        num_bucket = int(math.ceil(math.sqrt(n / self.BUCKET_RATIO)))
        self.a = [keys[n * i // num_bucket : n * (i + 1) // num_bucket] for i in range(num_bucket)]

    def __iter__(self) -> Iterator[K]:
        for a in self.a:
            for k in a:
                yield k

    def __reversed__(self) -> Iterator[K]:
        for a in reversed(self.a):
            for k in reversed(a):
                yield k

    def __len__(self) -> int:
        return self.size

    def __contains__(self, key: K) -> bool:
        return key in self.d

    def __getitem__(self, key: K) -> V:
        return self.d[key]

    def __setitem__(self, key: K, value: V) -> None:
        if key in self.d:
            self.d[key] = value
            return
        if self.size == 0:
            self.a = [[key]]
            self.d[key] = value
            self.size = 1
            return
        a, b, i = self._position(key)
        a.insert(i, key)
        self.d[key] = value
        self.size += 1
        if len(a) > len(self.a) * self.SPLIT_RATIO:
            mid = len(a) >> 1
            self.a[b:b+1] = [a[:mid], a[mid:]]

    def __delitem__(self, key: K) -> None:
        if key not in self.d:
            raise KeyError(key)
        a, b, i = self._position(key)
        self._pop_key(a, b, i)

    def __repr__(self) -> str:
        return "SortedDict({" + ", ".join(f"{k!r}: {self.d[k]!r}" for k in self) + "})"

    def _position(self, key: K) -> tuple[list[K], int, int]:
        "Return the bucket, bucket index, and lower-bound position for key. self must not be empty."
        for b, a in enumerate(self.a):
            if key <= a[-1]:
                break
        return a, b, bisect_left(a, key)

    def _pop_key(self, a: list[K], b: int, i: int) -> tuple[K, V]:
        key = a.pop(i)
        value = self.d.pop(key)
        self.size -= 1
        if not a:
            del self.a[b]
        return key, value

    def get(self, key: K, default=None):
        return self.d.get(key, default)

    def setdefault(self, key: K, default=None):
        if key in self.d:
            return self.d[key]
        self[key] = default
        return default

    def pop(self, key: K, *default):
        if key not in self.d:
            if default:
                if len(default) != 1:
                    raise TypeError(f"pop expected at most 2 arguments, got {2 + len(default)}")
                return default[0]
            raise KeyError(key)
        a, b, i = self._position(key)
        return self._pop_key(a, b, i)[1]

    def discard(self, key: K) -> bool:
        "Remove key and return True if removed."
        if key not in self.d:
            return False
        a, b, i = self._position(key)
        self._pop_key(a, b, i)
        return True

    def keys(self) -> Iterator[K]:
        return iter(self)

    def values(self) -> Iterator[V]:
        for k in self:
            yield self.d[k]

    def items(self) -> Iterator[tuple[K, V]]:
        for k in self:
            yield k, self.d[k]

    def lt(self, key: K) -> K | None:
        "Find the largest key < key, or None if it doesn't exist."
        for a in reversed(self.a):
            if a[0] < key:
                return a[bisect_left(a, key) - 1]

    def le(self, key: K) -> K | None:
        "Find the largest key <= key, or None if it doesn't exist."
        for a in reversed(self.a):
            if a[0] <= key:
                return a[bisect_right(a, key) - 1]

    def gt(self, key: K) -> K | None:
        "Find the smallest key > key, or None if it doesn't exist."
        for a in self.a:
            if a[-1] > key:
                return a[bisect_right(a, key)]

    def ge(self, key: K) -> K | None:
        "Find the smallest key >= key, or None if it doesn't exist."
        for a in self.a:
            if a[-1] >= key:
                return a[bisect_left(a, key)]

    def _item_at(self, i: int) -> tuple[K, V]:
        if i < 0:
            for a in reversed(self.a):
                i += len(a)
                if i >= 0:
                    k = a[i]
                    return k, self.d[k]
        else:
            for a in self.a:
                if i < len(a):
                    k = a[i]
                    return k, self.d[k]
                i -= len(a)
        raise IndexError

    def peekitem(self, i: int = -1) -> tuple[K, V]:
        "Return the i-th item in key order."
        return self._item_at(i)

    def popitem(self, i: int = -1) -> tuple[K, V]:
        "Pop and return the i-th item in key order."
        if i < 0:
            for b, a in enumerate(reversed(self.a)):
                i += len(a)
                if i >= 0:
                    return self._pop_key(a, ~b, i)
        else:
            for b, a in enumerate(self.a):
                if i < len(a):
                    return self._pop_key(a, b, i)
                i -= len(a)
        raise IndexError

    def index(self, key: K) -> int:
        "Count the number of keys < key."
        ans = 0
        for a in self.a:
            if a[-1] >= key:
                return ans + bisect_left(a, key)
            ans += len(a)
        return ans

    def index_right(self, key: K) -> int:
        "Count the number of keys <= key."
        ans = 0
        for a in self.a:
            if a[-1] > key:
                return ans + bisect_right(a, key)
            ans += len(a)
        return ans

    def lower_bound_cursor(self, key: K) -> "SortedDictCursor[K, V]":
        """Return the boundary just before the first item whose key >= key.
        Inserting or deleting keys invalidates existing cursors.
        """
        for b, a in enumerate(self.a):
            if a[-1] >= key:
                return SortedDictCursor(self, b, bisect_left(a, key))
        return SortedDictCursor(self, len(self.a), 0)

    def upper_bound_cursor(self, key: K) -> "SortedDictCursor[K, V]":
        """Return the boundary just before the first item whose key > key.
        Inserting or deleting keys invalidates existing cursors.
        """
        for b, a in enumerate(self.a):
            if a[-1] > key:
                return SortedDictCursor(self, b, bisect_right(a, key))
        return SortedDictCursor(self, len(self.a), 0)

    def erase(self, first: "SortedDictCursor[K, V]", last: "SortedDictCursor[K, V]") -> int:
        """Erase [first, last) in key order and return the number of erased items.
        The cursors must belong to self and must not have been invalidated.
        """
        if first.s is not self or last.s is not self:
            raise ValueError("cursor belongs to another SortedDict")
        b1, i1 = first.b, first.i
        b2, i2 = last.b, last.i
        if (b1, i1) > (b2, i2):
            raise ValueError("invalid cursor range")
        if (b1, i1) == (b2, i2):
            return 0

        a = self.a
        if b1 == b2:
            bucket = a[b1]
            keys = bucket[i1:i2]
            for k in keys:
                del self.d[k]
            n = len(keys)
            del bucket[i1:i2]
            self.size -= n
            if not bucket:
                del a[b1]
            return n

        left = a[b1]
        keys = left[i1:]
        for k in keys:
            del self.d[k]
        n = len(keys)
        del left[i1:]

        if b2 < len(a):
            right = a[b2]
            keys = right[:i2]
            for k in keys:
                del self.d[k]
            n += len(keys)
            del right[:i2]

            for bucket in a[b1 + 1:b2]:
                n += len(bucket)
                for k in bucket:
                    del self.d[k]

            keep = []
            if left:
                keep.append(left)
            if right:
                keep.append(right)
            a[b1:b2 + 1] = keep
        else:
            for bucket in a[b1 + 1:]:
                n += len(bucket)
                for k in bucket:
                    del self.d[k]
            a[b1:] = [left] if left else []

        self.size -= n
        return n


class SortedDictCursor(Generic[K, V]):
    """A cursor at a boundary between two items of a SortedDict."""

    __slots__ = ("s", "b", "i")

    def __init__(self, s: SortedDict[K, V], b: int, i: int) -> None:
        self.s = s
        self.b = b
        self.i = i

    def copy(self) -> "SortedDictCursor[K, V]":
        return SortedDictCursor(self.s, self.b, self.i)

    def prev(self) -> tuple[K, V] | None:
        "Return the item immediately before the cursor without moving it."
        a = self.s.a
        if self.b == len(a):
            if not a:
                return None
            k = a[-1][-1]
            return k, self.s.d[k]
        if self.i:
            k = a[self.b][self.i - 1]
            return k, self.s.d[k]
        if self.b:
            k = a[self.b - 1][-1]
            return k, self.s.d[k]

    def next(self) -> tuple[K, V] | None:
        "Return the item immediately after the cursor without moving it."
        if self.b == len(self.s.a):
            return None
        k = self.s.a[self.b][self.i]
        return k, self.s.d[k]

    def move_prev(self) -> bool:
        "Move one item to the left and return False if already at the beginning."
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
        "Move one item to the right and return False if already at the end."
        a = self.s.a
        if self.b == len(a):
            return False
        self.i += 1
        if self.i == len(a[self.b]):
            self.b += 1
            self.i = 0
        return True
