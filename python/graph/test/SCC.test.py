# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/scc

from python.graph.SCC import find_SCC


def main() -> None:
    n, m = map(int, input().split())
    g = [[] for _ in range(n)]
    for _ in range(m):
        a, b = map(int, input().split())
        g[a].append(b)

    groups, _, _ = find_SCC(g)
    print(len(groups))
    for group in groups:
        print(len(group), *group)


if __name__ == "__main__":
    main()
