# verification-helper: TITLE ランレングス圧縮

"""
ランレングス圧縮
"""

def run_length_encoding(S):
    prev = S[0]
    cnt = 0
    lst = []
    for v in S:
        if v == prev:
            cnt += 1
        else:
            lst.append((prev,cnt))
            cnt = 1
            prev = v
    lst.append((v,cnt))
    return lst
