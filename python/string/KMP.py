# competitive-verifier: TITLE KMP法
def prefix_function(s):
    """各接頭辞に対する KMP の失敗遷移表を、先頭を -1 として返す。"""
    n = len(s)
    table = [0]*(n+1)
    j = table[0] = -1
    for i in range(n):
        while j >= 0 and s[i] != s[j]:
            j = table[j]
        j += 1
        table[i+1] = j# if i+1 < n and s[i+1] != s[j] else table[j] # #を消すとKMP
    return table

def KMP(text,pattern,table):
    """重複を許して出現回数を返す。空パターンは len(text)+1 箇所に一致する。"""
    m = len(pattern)
    if m == 0: return len(text)+1
    cnt = k = 0
    for ti in text:
        while k >= 0 and pattern[k] != ti:
            k = table[k]
        k += 1
        if k >= m: #text[i-m+1:i+1] == pattern
            cnt += 1
            k = table[k]
    return cnt

  
  
