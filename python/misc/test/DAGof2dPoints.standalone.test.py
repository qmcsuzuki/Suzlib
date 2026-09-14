# competitive-verifier: STANDALONE

from itertools import product

from python.misc.DAGof2dPoints import DAGof2dPoints


if __name__ == "__main__":
    points = [(0,1),(0,0),(-1,0),(1,-1),(1,1)]
    for xr,yr in product([False,True],repeat=2):
        graph = DAGof2dPoints(points,xr,yr)
        for i,(x,y) in enumerate(points):
            seen = {i}
            queue = [i]
            for v in queue:
                for w in graph[v]:
                    if w not in seen:
                        seen.add(w)
                        queue.append(w)
            expected = {j for j,(xx,yy) in enumerate(points)
                        if (x >= xx if xr else x <= xx) and (y >= yy if yr else y <= yy)}
            assert seen.intersection(range(len(points))) == expected
