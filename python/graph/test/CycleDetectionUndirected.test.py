# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/cycle_detection_undirected

from python.graph.CycleDetection import find_cycle_undirected


def main():
    n, m = map(int, input().split())
    edges = [tuple(map(int, input().split())) for _ in range(m)]
    ok, vertices, edge_ids = find_cycle_undirected(n, edges)
    if not ok:
        print(-1)
    else:
        print(len(edge_ids))
        print(*vertices[:-1])
        print(*edge_ids)


if __name__ == "__main__":
    main()
