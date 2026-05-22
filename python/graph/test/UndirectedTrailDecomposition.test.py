# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/eulerian_trail_undirected

from python.graph.UndirectedTrailDecomposition import UndirectedTrailDecomposition


def main() -> None:
    T = int(input())
    for _ in range(T):
        n, m = map(int, input().split())
        edges = [tuple(map(int, input().split())) for _ in range(m)]
        dt = UndirectedTrailDecomposition(n, edges)
        ok, vertices, path = dt.eulerian_trail()
        if ok:
            print("Yes")
            print(*vertices)
            print(*path)
        else:
            print("No")


if __name__ == "__main__":
    main()
