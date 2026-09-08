# competitive-verifier: TITLE 最小回転
def minimum_rotation(s):
    """循環シフトのうち辞書順最小となる列を返す。"""
    a = 0
    b = 1
    n = len(s)
    s += s

    while b < n: # loop invariant: a is best in [0,b)
        for i in range(b-a):
            if s[a+i] > s[b+i]:
                a = b
                b += 1
                break
            if s[a+i] < s[b+i]:
                b += i + 1
                break
        else:
            b += b-a
    return s[a:a+n]
