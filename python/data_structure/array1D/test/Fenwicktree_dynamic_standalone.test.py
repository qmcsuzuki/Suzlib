# competitive-verifier: STANDALONE

from python.data_structure.array1D.FenwickTreeDinamic import FenwickTreeDinamic

if __name__ == "__main__":
    for n in range(1,20):
        bit = FenwickTreeDinamic(n)
        arr = [0]*n
        for i in range(n):
            bit.add(i,i+1)
            arr[i] += i+1

        for x in range(-3,sum(arr)+3):
            idx = bit.bisect_left(x)
            ok = next((i for i in range(n) if sum(arr[:i+1]) >= x), -1)
            assert idx == ok

        for x in range(-3, sum(arr)**2+3):
            idx = bit.bisect_left_key(x, key=lambda v: v*v)
            ok = next((i for i in range(n) if sum(arr[:i+1])**2 >= x), -1)
            assert idx == ok
