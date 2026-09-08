# competitive-verifier: STANDALONE

from random import Random

from python.string.SuffixArrayDoubling import suffix_array_functional_graph


if __name__ == "__main__":
    assert suffix_array_functional_graph([0],[99]) == ([0],[0])
    rng = Random(83)
    for n in range(1,15):
        for _ in range(40):
            nxt = [rng.randrange(n) for _ in range(n)]
            labels = [rng.randrange(4) for _ in range(n)]
            strings = []
            for v in range(n):
                s = []
                for _ in range(2*n):
                    s.append(labels[v])
                    v = nxt[v]
                strings.append(tuple(s))
            sa, rank = suffix_array_functional_graph(nxt,labels)
            uniq = sorted(set(strings))
            assert rank == [uniq.index(s) for s in strings]
            assert [strings[v] for v in sa] == sorted(strings)
