# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/cycle_detection

from python.graph.CycleDetection import find_cycle_directed


def main():
    n, m = map(int, input().split())
    edges = [tuple(map(int, input().split())) for _ in range(m)]
    ok, _, edge_ids = find_cycle_directed(n, edges)
    if not ok:
        print(-1)
    else:
        print(len(edge_ids))
        print(*edge_ids, sep="\n")


if __name__ == "__main__":
    main()
