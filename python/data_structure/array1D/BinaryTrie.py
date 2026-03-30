# competitive-verifier: TITLE Binary Trie（非負整数 multiset）


class BinaryTrie:
    """
    非負整数 multiset 用の binary trie. 各操作は O(MAX_BIT).
    """

    def __init__(self, max_bit=30):
        """
        max_bit:
            扱う整数の最大 bit 位置.
            例えば 0 <= x < 2^30 なら max_bit=29 で十分.
        """
        self.MAX_BIT = max_bit
        self.SHIFT = 30
        self.MASK = (1 << self.SHIFT) - 1
        # child[v] = ch0[v] + (ch1[v] << SHIFT)
        self.child = [0, 0]  # 0: null, 1: root
        self.size = [0, 0]   # 部分木のサイズ

    def __len__(self):
        """
        # multiset 全体の要素数を返す.
        """
        return self.size[1]

    def _new_node(self):
        """
        新しいノードを 1 つ作って、その index を返す.
        """
        self.child.append(0)
        self.size.append(0)
        return len(self.size) - 1

    def _ch0(self, v):
        return self.child[v] & self.MASK

    def _ch1(self, v):
        return self.child[v] >> self.SHIFT

    def _set_ch0(self, v, nv):
        self.child[v] = (self.child[v] & (~self.MASK)) | nv

    def _set_ch1(self, v, nv):
        self.child[v] = (self.child[v] & self.MASK) | (nv << self.SHIFT)

    def add(self, x, k=1):
        """
        値 x を k 個追加する.
        """
        if k <= 0:
            return
        v = 1
        self.size[v] += k
        for b in range(self.MAX_BIT, -1, -1):
            if (x >> b) & 1:
                nv = self._ch1(v)
                if nv == 0:
                    nv = self._new_node()
                    self._set_ch1(v, nv)
            else:
                nv = self._ch0(v)
                if nv == 0:
                    nv = self._new_node()
                    self._set_ch0(v, nv)
            v = nv
            self.size[v] += k

    def count(self, x):
        """
        値 x の個数を返す.
        存在しなければ 0.
        """
        v = 1
        for b in range(self.MAX_BIT, -1, -1):
            v = self._ch1(v) if ((x >> b) & 1) else self._ch0(v)
            if v == 0:
                return 0
        return self.size[v]

    def discard(self, x, k=1):
        """
        値 x を k 個削除する.
        個数が足りなければ何もせず False を返す.
        成功したら True.
        """
        if k <= 0:
            return True
        if self.count(x) < k:
            return False
        v = 1
        self.size[v] -= k
        for b in range(self.MAX_BIT, -1, -1):
            v = self._ch1(v) if ((x >> b) & 1) else self._ch0(v)
            self.size[v] -= k
        return True

    def remove(self, x, k=1):
        """
        値 x を k 個削除する.
        個数が足りなければ KeyError.
        """
        if not self.discard(x, k):
            raise KeyError(x)

    def get_min(self):
        """
        multiset 内の最小値を返す.
        空なら IndexError.
        """
        if self.size[1] == 0:
            raise IndexError("BinaryTrie is empty")
        v = 1
        ans = 0
        for b in range(self.MAX_BIT, -1, -1):
            nv = self._ch0(v)
            if nv and self.size[nv] > 0:
                v = nv
            else:
                v = self._ch1(v)
                ans |= 1 << b
        return ans

    def get_max(self):
        """
        multiset 内の最大値を返す.
        空なら IndexError.
        """
        if self.size[1] == 0:
            raise IndexError("BinaryTrie is empty")
        v = 1
        ans = 0
        for b in range(self.MAX_BIT, -1, -1):
            nv = self._ch1(v)
            if nv and self.size[nv] > 0:
                v = nv
                ans |= 1 << b
            else:
                v = self._ch0(v)
        return ans

    def pop_min(self):
        """
        最小値を 1 個取り出して削除し、その値を返す.
        空なら IndexError.
        """
        x = self.get_min()
        self.discard(x)
        return x

    def pop_max(self):
        """
        最大値を 1 個取り出して削除し、その値を返す.
        空なら IndexError.
        """
        x = self.get_max()
        self.discard(x)
        return x

    def kth(self, k):
        """
        0-indexed で k 番目に小さい値を返す.
        例えば kth(0) は最小値.
        範囲外なら IndexError.
        """
        if not (0 <= k < self.size[1]):
            raise IndexError("k out of range")
        v = 1
        ans = 0
        for b in range(self.MAX_BIT, -1, -1):
            lc = self._ch0(v)
            left_cnt = self.size[lc] if lc else 0
            if k < left_cnt:
                v = lc
            else:
                k -= left_cnt
                v = self._ch1(v)
                ans |= 1 << b
        return ans

    def bisect_left(self, x):
        """
        x より小さい要素の個数を返す.
        sorted multiset に対する bisect_left と同様.
        """
        if x <= 0:
            return 0
        res = 0
        v = 1
        for b in range(self.MAX_BIT, -1, -1):
            if v == 0:
                break
            if (x >> b) & 1:
                lc = self._ch0(v)
                if lc:
                    res += self.size[lc]
                v = self._ch1(v)
            else:
                v = self._ch0(v)
        return res

    def xor_bisect_left(self, x, k):
        """
        x xor y < k を満たす y in multiset の個数を返す.
        すなわち #{y | x ^ y < k}.
        """
        if k <= 0:
            return 0

        # trie が管理していない上位 bit を先に処理する
        hi = self.MAX_BIT + 1
        xh = x >> hi
        kh = k >> hi
        if xh < kh:
            return self.size[1]
        if xh > kh:
            return 0

        res = 0
        v = 1
        for b in range(self.MAX_BIT, -1, -1):
            if v == 0:
                break

            xb = (x >> b) & 1
            kb = (k >> b) & 1
            if kb == 1:
                # この bit で xor bit = 0 を選ぶと、ここで初めて k より小さくなる
                same = self._ch1(v) if xb else self._ch0(v)
                if same:
                    res += self.size[same]

                # 等号を保つには xor bit = 1 を選んで進む
                v = self._ch0(v) if xb else self._ch1(v)
            else:  # xor bit = 0 しか許されない
                v = self._ch1(v) if xb else self._ch0(v)

        return res

    def min_xor_element(self, x):
        """
        multiset 内の要素 y のうち、
        x xor y を最小にするような y を返す.
        空なら IndexError.
        """
        if self.size[1] == 0:
            raise IndexError("BinaryTrie is empty")
        v = 1
        ans = 0
        for b in range(self.MAX_BIT, -1, -1):
            bit = (x >> b) & 1
            preferred = self._ch1(v) if bit else self._ch0(v)
            other = self._ch0(v) if bit else self._ch1(v)
            if preferred and self.size[preferred] > 0:
                v = preferred
                if bit:
                    ans |= 1 << b
            else:
                v = other
                if bit ^ 1:
                    ans |= 1 << b
        return ans

    def min_xor_value(self, x):
        """
        multiset 内の要素 y に対する min(x xor y) の値を返す.
        空なら IndexError.
        """
        return self.min_xor_element(x) ^ x

    def max_xor_element(self, x):
        """
        multiset 内の要素 y のうち、
        x xor y を最大にするような y を返す.
        空なら IndexError.
        """
        if self.size[1] == 0:
            raise IndexError("BinaryTrie is empty")
        v = 1
        ans = 0
        for b in range(self.MAX_BIT, -1, -1):
            bit = (x >> b) & 1
            preferred = self._ch0(v) if bit else self._ch1(v)
            other = self._ch1(v) if bit else self._ch0(v)
            if preferred and self.size[preferred] > 0:
                v = preferred
                if bit ^ 1:
                    ans |= 1 << b
            else:
                v = other
                if bit:
                    ans |= 1 << b
        return ans

    def max_xor_value(self, x):
        """
        multiset 内の要素 y に対する max(x xor y) の値を返す.
        空なら IndexError.
        """
        return self.max_xor_element(x) ^ x
