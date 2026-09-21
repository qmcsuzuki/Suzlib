# competitive-verifier: PROBLEM https://judge.yosupo.jp/problem/assignment

from python.graph.Assignment import assignment


def main() -> None:
    n = int(input())
    cost = [list(map(int, input().split())) for _ in range(n)]
    min_cost, match = assignment(cost)
    print(min_cost)
    print(*match)


if __name__ == "__main__":
    main()
