# verification-helper: PROBLEM https://judge.yosupo.jp/problem/eulerian_trail_undirected

from python.graph.EulerianTrail import Eulerian_trail_undirected


def main() -> None:
    T = int(input())
    for _ in range(T):
        n, m = map(int, input().split())
        edges = [tuple(map(int, input().split())) for _ in range(m)]
        ok, vertices, path = Eulerian_trail_undirected(n, edges)
        if ok:
            print("Yes")
            print(*vertices)
            print(*path)
        else:
            print("No")


if __name__ == "__main__":
    main()
