def prefix_function(s):
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
    m = len(pattern)
    cnt = k = 0
    for ti in text:
        while k >= 0 and pattern[k] != ti:
            k = table[k]
        k += 1
        if k >= m: #text[i-m+1:i+1] == pattern
            cnt += 1
            k = table[k]
    return cnt

  
  
