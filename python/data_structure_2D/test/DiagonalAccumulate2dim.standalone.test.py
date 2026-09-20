# competitive-verifier: STANDALONE

from random import Random

from python.data_structure_2D.DiagonalAccumulate2dim import DiagonalAccumulate2dim


if __name__ == "__main__":
    rng = Random(0)

    for h in range(1, 6):
        for w in range(1, 6):
            for _ in range(10):
                a = [[rng.randrange(-10, 11) for _ in range(w)] for _ in range(h)]
                acc = DiagonalAccumulate2dim(a)

                # check diagonal range sum against brute force
                for _ in range(100):
                    p, q = sorted((rng.randrange(-w - 2, h + w + 2),
                                   rng.randrange(-w - 2, h + w + 2)))
                    r, s = sorted((rng.randrange(-w - 2, h + 2),
                                   rng.randrange(-w - 2, h + 2)))
                    expected = sum(
                        a[x][y]
                        for x in range(h)
                        for y in range(w)
                        if p <= x + y < q and r <= x - y < s
                    )
                    assert acc.range_sum(p, q, r, s) == expected

                # x is downward and y is rightward, as in matrix coordinates.
                # Check four inclusive diagonal regions against brute force.
                for x in range(h):
                    for y in range(w):
                        up = right = down = left = 0
                        for i in range(h):
                            for j in range(w):
                                v = a[i][j]
                                dx = i - x
                                dy = j - y
                                if -dx >= abs(dy):
                                    up += v
                                if dy >= abs(dx):
                                    right += v
                                if dx >= abs(dy):
                                    down += v
                                if -dy >= abs(dx):
                                    left += v
                        assert acc.up(x, y) == up
                        assert acc.right(x, y) == right
                        assert acc.down(x, y) == down
                        assert acc.left(x, y) == left
